from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import HavalApi
from .const import CONF_USERNAME, CONF_PASSWORD

class HavalDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        session = async_get_clientsession(hass)
        self.api = HavalApi(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            session,
        )
        super().__init__(hass, None, update_interval=timedelta(minutes=10))

    async def _async_update_data(self):
        return await self.api.fetch_vehicle_data()