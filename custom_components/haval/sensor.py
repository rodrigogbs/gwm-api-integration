from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HavalSensor(coordinator, "battery", "Bateria", "%"),
        HavalSensor(coordinator, "range_km", "Autonomia", "km"),
    ])

class HavalSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Haval {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{coordinator.data['vin']}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.data["vin"])},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": "Haval Vehicle",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)