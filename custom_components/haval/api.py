import logging
_LOGGER = logging.getLogger(__name__)

class HavalApi:
    def __init__(self, username, password, session):
        self.username = username
        self.password = password
        self.session = session

    async def authenticate(self):
        _LOGGER.info("Mock login realizado")

    async def fetch_vehicle_data(self):
        return {
            "battery": 80,
            "range_km": 420,
            "doors_locked": True,
            "latitude": -23.55,
            "longitude": -46.63,
            "climate_on": False,
        }

    async def set_climate(self, state: bool):
        _LOGGER.info("Set climate %s", state)

    async def set_lock(self, state: bool):
        _LOGGER.info("Set lock %s", state)