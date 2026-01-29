from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import HavalApi
from .const import CONF_USERNAME, CONF_PASSWORD, CONF_CHASSIS, DEFAULT_POLL_SECONDS
from .exceptions import HavalAuthError, HavalApiError

class HavalCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry

        self.api = HavalApi(
            session=async_get_clientsession(hass),
            hass=hass,
            username=entry.data[CONF_USERNAME],
            password_plain=entry.data[CONF_PASSWORD],
            chassis=entry.data[CONF_CHASSIS],
        )
        self.vin: str | None = None

        super().__init__(
            hass,
            logger=None,
            name="Haval / GWM",
            update_interval=timedelta(seconds=DEFAULT_POLL_SECONDS),
        )

    async def async_initialize(self) -> None:
        await self.api.login()
        self.vin = await self.api.acquire_vehicles()
        await self.async_config_entry_first_refresh()

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.api.get_last_status(self.vin)
        except (HavalAuthError, HavalApiError):
            await self.api.login()
            self.vin = await self.api.acquire_vehicles()
            return await self.api.get_last_status(self.vin)
