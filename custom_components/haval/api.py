from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional

import async_timeout
from aiohttp import ClientSession, ClientError
from homeassistant.core import HomeAssistant

from .const import AUTH_BASE, APP_BASE
from .exceptions import HavalAuthError, HavalApiError


# WAF workaround:
# Some environments (notably HA Core's Python TLS fingerprint) may get the connection closed (Empty reply).
# Using curl_cffi (curl-impersonate) often matches browser/mobile TLS fingerprints and avoids that behavior.
try:
    from curl_cffi import requests as crequests  # type: ignore
except Exception:  # pragma: no cover
    crequests = None  # type: ignore


COMMON_HTTP_HEADERS = {
    "accept": "application/json",
    "user-agent": "okhttp/4.9.3",
}

HEADERS_AUTH = {
    **COMMON_HTTP_HEADERS,
    "appid": "6",
    "brand": "6",
    "brandid": "CCZ001",
    "country": "BR",
    "devicetype": "0",
    "enterpriseid": "CC01",
    "gwid": "",
    "language": "pt_BR",
    "rs": "5",
    "terminal": "GW_PC_GWM",
}

HEADERS_APP_BASE = {
    **COMMON_HTTP_HEADERS,
    "rs": "2",
    "terminal": "GW_APP_GWM",
    "brand": "6",
    "language": "pt_BR",
    "systemtype": "2",
    "regioncode": "BR",
    "country": "BR",
}


def _md5_hex(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


class HavalApi:
    def __init__(self, session: ClientSession, hass: HomeAssistant, username: str, password_plain: str, chassis: str):
        self._session = session
        self._hass = hass
        self._username = username
        self._password_md5 = _md5_hex(password_plain)
        self._chassis = chassis
        self._device_id = chassis  # per Postman: deviceid == {{chassis}}

        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.vin: Optional[str] = None

    async def login(self) -> None:
        payload = {"deviceid": self._device_id, "password": self._password_md5, "account": self._username}
        try:
            async with async_timeout.timeout(30):
                async with self._session.post(
                    f"{AUTH_BASE}/userAuth/loginAccount",
                    headers=HEADERS_AUTH,
                    json=payload,
                ) as resp:
                    j = await resp.json(content_type=None)
        except (ClientError, TimeoutError) as e:
            raise HavalAuthError(f"Network error during login: {e}") from e
        except Exception as e:
            raise HavalAuthError(str(e)) from e

        try:
            data = j.get("data") or {}
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
        except Exception as e:
            raise HavalAuthError(f"Unexpected login response: {j}") from e

    def _app_headers(self) -> Dict[str, str]:
        if not self.access_token or not self.refresh_token:
            raise HavalAuthError("Missing tokens")
        h = dict(HEADERS_APP_BASE)
        h["accessToken"] = self.access_token
        h["refreshToken"] = self.refresh_token
        return h

    async def _curl_json(self, method: str, url: str, *, headers: Dict[str, str], params: Dict[str, Any] | None = None, json_body: Any | None = None) -> Any:
        if crequests is None:
            raise HavalApiError("curl-cffi not available to bypass WAF/TLS fingerprint issues")

        def _do():
            resp = crequests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
                impersonate="chrome",  # good default; can be changed if needed
            )
            # Accept 200-499 as "response"; raise only on network-level issues.
            return resp.status_code, resp.text, resp.headers

        status, text, _hdrs = await self._hass.async_add_executor_job(_do)
        try:
            import json as _json
            return _json.loads(text) if text else {}
        except Exception:
            # If server returns HTML or empty, keep raw snippet
            raise HavalApiError(f"Non-JSON response (status={status}): {text[:200]}")

    async def acquire_vehicles(self) -> str:
        # Prefer curl_cffi for APP gateway (most likely to be WAF-blocked for aiohttp)
        try:
            j = await self._curl_json(
                "GET",
                f"{APP_BASE}globalapp/vehicle/acquireVehicles",
                headers=self._app_headers(),
            )
        except HavalApiError:
            # Fallback to aiohttp (works in some environments)
            try:
                async with async_timeout.timeout(30):
                    async with self._session.get(
                        f"{APP_BASE}globalapp/vehicle/acquireVehicles",
                        headers=self._app_headers(),
                    ) as resp:
                        j = await resp.json(content_type=None)
            except (ClientError, TimeoutError) as e:
                raise HavalApiError(f"Network error during acquireVehicles: {e}") from e

        try:
            vin = (j.get("data") or [])[0]["vin"]
        except Exception:
            vin = self._chassis

        self.vin = vin
        return vin

    async def get_last_status(self, vin: Optional[str] = None) -> Dict[str, Any]:
        vin = vin or self.vin or self._chassis
        try:
            j = await self._curl_json(
                "GET",
                f"{APP_BASE}vehicle/getLastStatus",
                headers=self._app_headers(),
                params={"vin": vin},
            )
            return j.get("data") or {}
        except HavalApiError:
            # fallback aiohttp
            try:
                async with async_timeout.timeout(30):
                    async with self._session.get(
                        f"{APP_BASE}vehicle/getLastStatus",
                        headers=self._app_headers(),
                        params={"vin": vin},
                    ) as resp:
                        j = await resp.json(content_type=None)
                return j.get("data") or {}
            except (ClientError, TimeoutError) as e:
                raise HavalApiError(f"Network error during getLastStatus: {e}") from e

    async def send_cmd_ac(self, *, vin: Optional[str], command_password_plain: str, enable: bool, temperature_c: int = 18) -> Dict[str, Any]:
        vin = vin or self.vin or self._chassis
        if not command_password_plain:
            raise HavalApiError("Command password not configured")

        security_password = _md5_hex(command_password_plain)
        seq_no = str(int(time.time() * 1000))

        body = {
            "instructions": {"0x04": {"airConditioner": {"operationTime": "0", "switchOrder": "1" if enable else "0", "temperature": str(int(temperature_c))}}},
            "remoteType": "0",
            "securityPassword": security_password,
            "seqNo": seq_no,
            "type": "1",
            "vin": vin,
        }

        # Commands also go through APP gateway — use curl_cffi first
        j = await self._curl_json(
            "POST",
            f"{APP_BASE}vehicle/T5/sendCmd",
            headers=self._app_headers(),
            json_body=body,
        )
        return j
