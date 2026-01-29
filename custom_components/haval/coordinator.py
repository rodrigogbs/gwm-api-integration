from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import HavalApi
from .const import CONF_USERNAME, CONF_PASSWORD, CONF_DEVICE_ID, DEFAULT_POLL_SECONDS
from .exceptions import HavalAuthError


class HavalCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry

        self.api = HavalApi(
            session=async_get_clientsession(hass),
            username=entry.data[CONF_USERNAME],
            password_plain=entry.data[CONF_PASSWORD],
            device_id=entry.data[CONF_DEVICE_ID],
        )

        self.vin: str | None = None
        self.basics: Dict[str, Any] = {}

        super().__init__(
            hass,
            logger=None,
            name="Haval / GWM",
            update_interval=timedelta(seconds=DEFAULT_POLL_SECONDS),
        )

    async def async_initialize(self) -> None:
        # Login + get VIN once at startup
        await self.api.login()
        self.vin = await self.api.acquire_vehicles()
        self.basics = await self.api.get_vehicle_basics(self.vin)
        await self.async_config_entry_first_refresh()

    async def _async_update_data(self) -> Dict[str, Any]:
        # If tokens expire, simplest reliable approach is re-login (API may change refresh semantics)
        try:
            return await self.api.get_last_status(self.vin)
        except HavalAuthError:
            await self.api.login()
            await self.api.acquire_vehicles()
            return await self.api.get_last_status(self.vin)
