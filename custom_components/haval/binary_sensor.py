
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalDoorSensor(coord)])

class HavalDoorSensor(CoordinatorEntity, BinarySensorEntity):
    @property
    def is_on(self):
        return self.coordinator.data.get("doors_locked")
