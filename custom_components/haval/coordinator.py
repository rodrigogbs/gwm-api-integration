from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import HavalApi
from .const import CONF_USERNAME, CONF_PASSWORD
import aiohttp

class HavalDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.api = HavalApi(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            aiohttp.ClientSession(),
        )
        super().__init__(hass, None, update_interval=timedelta(minutes=5))

    async def _async_update_data(self):
        return await self.api.fetch_vehicle_data()