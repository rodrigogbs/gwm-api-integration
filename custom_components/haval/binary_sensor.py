from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalBinarySensor(coordinator)])

class HavalBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Haval Portas Trancadas"
        self._attr_unique_id = f"{coordinator.data['vin']}_doors"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.data["vin"])},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": "Haval Vehicle",
        }

    @property
    def is_on(self):
        return self.coordinator.data.get("doors_locked")