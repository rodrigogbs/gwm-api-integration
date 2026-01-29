from homeassistant.components.device_tracker import TrackerEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalTracker(coordinator)])

class HavalTracker(TrackerEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Haval Localização"

    @property
    def latitude(self):
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self):
        return self.coordinator.data.get("longitude")