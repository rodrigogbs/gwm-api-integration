from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .util import get_first


async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HavalSensor(coord, "battery", "Bateria", "%", ["soc", "battery", "bms.soc", "vehicleStatus.soc"]),
            HavalSensor(coord, "range", "Autonomia", "km", ["range", "rangeKm", "bms.range", "vehicleStatus.range"]),
            HavalSensor(coord, "odometer", "Odômetro", "km", ["totalMileage", "mileage", "odometer", "vehicleStatus.totalMileage"]),
            HavalRawStatusSensor(coord),
        ]
    )


class _Base(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        vin = getattr(coordinator, "vin", None) or "unknown"
        self._vin = vin
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vin)},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": f"Haval {vin}",
        }


class HavalSensor(_Base, SensorEntity):
    def __init__(self, coordinator, key, name, unit, paths):
        super().__init__(coordinator)
        self._key = key
        self._paths = paths
        self._attr_name = f"Haval {name}"
        self._attr_unique_id = f"{self._vin}_{key}"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return get_first(self.coordinator.data, self._paths)


class HavalRawStatusSensor(_Base, SensorEntity):
    _attr_name = "Haval Status (raw)"
    _attr_icon = "mdi:car-connected"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_raw_status"

    @property
    def native_value(self):
        # Keep short value; full payload goes in attributes
        return "ok" if self.coordinator.data else "unknown"

    @property
    def extra_state_attributes(self):
        return {"status": self.coordinator.data, "basics": getattr(self.coordinator, "basics", {})}
