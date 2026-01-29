
import aiohttp
import async_timeout
from datetime import datetime, timedelta
from .const import BASE_URL

class HavalApi:
    def __init__(self, username, password, session):
        self._username = username
        self._password = password
        self._session = session
        self._access_token = None
        self._refresh_token = None
        self._token_expiry = None

    async def authenticate(self):
        async with async_timeout.timeout(30):
            async with self._session.post(
                f"{BASE_URL}/auth/login",
                json={
                    "username": self._username,
                    "password": self._password
                }
            ) as resp:
                data = await resp.json()
                self._access_token = data["access_token"]
                self._refresh_token = data["refresh_token"]
                self._token_expiry = datetime.utcnow() + timedelta(seconds=data["expires_in"])

    async def _ensure_token(self):
        if not self._access_token or datetime.utcnow() >= self._token_expiry:
            await self.refresh_token()

    async def refresh_token(self):
        async with self._session.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": self._refresh_token}
        ) as resp:
            data = await resp.json()
            self._access_token = data["access_token"]
            self._token_expiry = datetime.utcnow() + timedelta(seconds=data["expires_in"])

    async def _request(self, method, endpoint, json=None):
        await self._ensure_token()
        headers = {"Authorization": f"Bearer {self._access_token}"}

        async with self._session.request(
            method,
            f"{BASE_URL}{endpoint}",
            headers=headers,
            json=json
        ) as resp:
            return await resp.json()

    async def get_vehicle_status(self):
        return await self._request("GET", "/vehicle/status")

    async def lock_doors(self, locked: bool):
        return await self._request(
            "POST",
            "/vehicle/lock",
            json={"locked": locked}
        )

    async def set_climate(self, enabled: bool):
        return await self._request(
            "POST",
            "/vehicle/climate",
            json={"enabled": enabled}
        )
