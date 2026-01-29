from __future__ import annotations

from homeassistant.components.device_tracker import TrackerEntity, SourceType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .util import get_first


async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalTracker(coord)])


class HavalTracker(CoordinatorEntity, TrackerEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        vin = getattr(coordinator, "vin", None) or "unknown"
        self._vin = vin
        self._attr_name = "Haval Localização"
        self._attr_unique_id = f"{vin}_location"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vin)},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": f"Haval {vin}",
        }

    @property
    def source_type(self):
        return SourceType.GPS

    @property
    def latitude(self):
        return get_first(self.coordinator.data, ["latitude", "gps.latitude", "location.lat", "vehicleStatus.latitude"])

    @property
    def longitude(self):
        return get_first(self.coordinator.data, ["longitude", "gps.longitude", "location.lng", "vehicleStatus.longitude"])
