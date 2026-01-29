import logging
_LOGGER = logging.getLogger(__name__)

class HavalApi:
    def __init__(self, username, password, session):
        self.username = username
        self.password = password
        self.session = session

    async def authenticate(self):
        _LOGGER.debug("Mock authentication successful")

    async def fetch_vehicle_data(self):
        return {
            "vin": "MOCKVIN123",
            "battery": 82,
            "range_km": 430,
            "doors_locked": True,
            "latitude": -23.55,
            "longitude": -46.63,
            "climate_on": False,
        }

    async def set_lock(self, state: bool):
        _LOGGER.debug("Set lock %s", state)

    async def set_climate(self, state: bool):
        _LOGGER.debug("Set climate %s", state)