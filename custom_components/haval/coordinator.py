
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import HavalApi
from .const import CONF_USERNAME, CONF_PASSWORD

class HavalDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.api = HavalApi(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            async_get_clientsession(hass),
        )
        super().__init__(
            hass,
            logger=None,
            update_interval=timedelta(minutes=5),
        )

    async def async_initialize(self):
        await self.api.authenticate()
        await self.async_refresh()

    async def _async_update_data(self):
        return await self.api.get_vehicle_status()
