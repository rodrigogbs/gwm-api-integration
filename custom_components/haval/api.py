from __future__ import annotations

import hashlib
import time
import logging
from typing import Any, Dict, Optional

import async_timeout
from aiohttp import ClientSession, ClientError
from homeassistant.core import HomeAssistant

from .const import AUTH_BASE, APP_BASE
from .exceptions import HavalAuthError, HavalApiError

_LOGGER = logging.getLogger(__name__)

try:
    from curl_cffi import requests as crequests  # type: ignore
except Exception as e:  # pragma: no cover
    crequests = None  # type: ignore
    _LOGGER.error("curl-cffi unavailable (cannot bypass APP gateway WAF): %s", e)


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
        self._device_id = chassis  # deviceid == chassis (per Postman)

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
                    text = await resp.text()
                    _LOGGER.debug("Login HTTP %s ct=%s body_prefix=%s", resp.status, resp.headers.get("content-type"), text[:200])
                    try:
                        j = await resp.json(content_type=None)
                    except Exception as e:
                        raise HavalAuthError(f"Login returned non-JSON (status={resp.status}): {text[:200]}") from e
        except (ClientError, TimeoutError) as e:
            raise HavalAuthError(f"Network error during login: {e}") from e
        except Exception as e:
            raise HavalAuthError(str(e)) from e

        try:
            data = j.get("data") or {}
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
            _LOGGER.debug("Login OK: tokens acquired")
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
            raise HavalApiError("curl-cffi not installed/available; APP gateway likely to drop Python TLS clients")

        impersonations = ["chrome", "safari_ios", "chrome_android", "edge"]
        last_err: Exception | None = None

        def _do(imp: str):
            resp = crequests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
                impersonate=imp,
            )
            return resp.status_code, resp.text

        for imp in impersonations:
            try:
                status, text = await self._hass.async_add_executor_job(_do, imp)
                _LOGGER.debug("curl-cffi[%s] %s %s -> %s body_prefix=%s", imp, method, url, status, (text or "")[:200])
                try:
                    import json as _json
                    return _json.loads(text) if text else {}
                except Exception as e:
                    last_err = e
                    # Keep trying other impersonations if response isn't JSON
                    continue
            except Exception as e:
                last_err = e
                continue

        raise HavalApiError(f"curl-cffi failed for {url}: {last_err}")

    async def acquire_vehicles(self) -> str:
        url = f"{APP_BASE}globalapp/vehicle/acquireVehicles"
        j = await self._curl_json("GET", url, headers=self._app_headers())
        try:
            vin = (j.get("data") or [])[0]["vin"]
        except Exception:
            vin = self._chassis
        self.vin = vin
        return vin

    async def get_last_status(self, vin: Optional[str] = None) -> Dict[str, Any]:
        vin = vin or self.vin or self._chassis
        url = f"{APP_BASE}vehicle/getLastStatus"
        j = await self._curl_json("GET", url, headers=self._app_headers(), params={"vin": vin})
        return j.get("data") or {}

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
        url = f"{APP_BASE}vehicle/T5/sendCmd"
        return await self._curl_json("POST", url, headers=self._app_headers(), json_body=body)
