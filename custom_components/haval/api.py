from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional

import async_timeout
from aiohttp import ClientSession

from .const import AUTH_BASE, APP_BASE
from .exceptions import HavalAuthError, HavalApiError


HEADERS_AUTH = {
    "appid": "6",
    "brand": "6",
    "brandid": "CCZ001",
    "country": "BR",
    "devicetype": "0",
    "enterpriseid": "CC01",
    "language": "pt_BR",
    "terminal": "GW_PC_GWM",
}

HEADERS_APP_BASE = {
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
    """HTTP client for GWM/Haval endpoints (no MQTT)."""

    def __init__(self, session: ClientSession, username: str, password_plain: str, device_id: str):
        self._session = session
        self._username = username
        self._password_md5 = _md5_hex(password_plain)
        self._device_id = device_id

        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.vin: Optional[str] = None

    async def login(self) -> None:
        payload = {
            "deviceid": self._device_id,
            "password": self._password_md5,
            "account": self._username,
        }
        try:
            async with async_timeout.timeout(30):
                async with self._session.post(
                    f"{AUTH_BASE}/userAuth/loginAccount",
                    headers=HEADERS_AUTH,
                    json=payload,
                ) as resp:
                    j = await resp.json(content_type=None)
        except Exception as e:
            raise HavalAuthError(str(e)) from e

        # Expected: j["data"]["accessToken"], j["data"]["refreshToken"]
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

    async def acquire_vehicles(self) -> str:
        async with async_timeout.timeout(30):
            async with self._session.get(
                f"{APP_BASE}globalapp/vehicle/acquireVehicles",
                headers=self._app_headers(),
            ) as resp:
                j = await resp.json(content_type=None)
        try:
            vin = j["data"][0]["vin"]
        except Exception as e:
            raise HavalApiError(f"Unexpected acquireVehicles response: {j}") from e
        self.vin = vin
        return vin

    async def get_last_status(self, vin: Optional[str] = None) -> Dict[str, Any]:
        vin = vin or self.vin
        if not vin:
            raise HavalApiError("VIN is not set")
        async with async_timeout.timeout(30):
            async with self._session.get(
                f"{APP_BASE}vehicle/getLastStatus",
                headers=self._app_headers(),
                params={"vin": vin},
            ) as resp:
                j = await resp.json(content_type=None)
        return j.get("data") or {}

    async def get_vehicle_basics(self, vin: Optional[str] = None) -> Dict[str, Any]:
        vin = vin or self.vin
        if not vin:
            raise HavalApiError("VIN is not set")
        async with async_timeout.timeout(30):
            async with self._session.get(
                f"{APP_BASE}vehicle/vehicleBasicsInfo",
                headers=self._app_headers(),
                params={"vin": vin, "flag": "true"},
            ) as resp:
                j = await resp.json(content_type=None)
        return j.get("data") or {}

    async def get_charge_logs(self) -> Dict[str, Any]:
        async with async_timeout.timeout(30):
            async with self._session.post(
                f"{APP_BASE}vehicleCharge/getChargeLogs",
                headers=self._app_headers(),
                json={},  # Postman body empty
            ) as resp:
                j = await resp.json(content_type=None)
        return j.get("data") or {}

    async def send_cmd_ac(self, *, vin: Optional[str], command_password_plain: str, enable: bool, temperature_c: int = 18) -> Dict[str, Any]:
        """Send A/C command using the same structure as Postman collection."""
        vin = vin or self.vin
        if not vin:
            raise HavalApiError("VIN is not set")
        if not command_password_plain:
            raise HavalApiError("Command password not configured")

        security_password = _md5_hex(command_password_plain)
        seq_no = str(int(time.time() * 1000))

        body = {
            "instructions": {
                "0x04": {
                    "airConditioner": {
                        "operationTime": "0",
                        "switchOrder": "1" if enable else "0",
                        "temperature": str(int(temperature_c)),
                    }
                }
            },
            "remoteType": "0",
            "securityPassword": security_password,
            "seqNo": seq_no,
            "type": "1",
            "vin": vin,
        }

        async with async_timeout.timeout(30):
            async with self._session.post(
                f"{APP_BASE}vehicle/T5/sendCmd",
                headers=self._app_headers(),
                json=body,
            ) as resp:
                j = await resp.json(content_type=None)
        return j
