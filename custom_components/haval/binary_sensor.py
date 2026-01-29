from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalBinarySensor(coordinator)])

class HavalBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Haval Portas Trancadas"

    @property
    def is_on(self):
        return self.coordinator.data.get("doors_locked")