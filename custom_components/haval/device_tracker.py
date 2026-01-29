from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalTracker(coordinator)])

class HavalTracker(CoordinatorEntity, TrackerEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Haval Localização"
        self._attr_unique_id = f"{coordinator.data['vin']}_location"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.data["vin"])},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": "Haval Vehicle",
        }

    @property
    def latitude(self):
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self):
        return self.coordinator.data.get("longitude")