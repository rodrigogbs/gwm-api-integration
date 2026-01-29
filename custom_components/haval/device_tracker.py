
from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data["haval"][entry.entry_id]
    async_add_entities([HavalTracker(coord)])

class HavalTracker(CoordinatorEntity, TrackerEntity):
    @property
    def latitude(self):
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self):
        return self.coordinator.data.get("longitude")
