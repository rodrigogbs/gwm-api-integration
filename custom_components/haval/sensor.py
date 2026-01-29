from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HavalSensor(coordinator, "Bateria", "battery", "%"),
        HavalSensor(coordinator, "Autonomia", "range_km", "km"),
    ])

class HavalSensor(SensorEntity):
    def __init__(self, coordinator, name, key, unit):
        self.coordinator = coordinator
        self._attr_name = f"Haval {name}"
        self.key = key
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)