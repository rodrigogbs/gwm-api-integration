from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalClimate(coordinator)])

class HavalClimate(CoordinatorEntity, ClimateEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Haval Ar-Condicionado"
        self._attr_unique_id = f"{coordinator.data['vin']}_climate"
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.data["vin"])},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": "Haval Vehicle",
        }

    @property
    def hvac_mode(self):
        return HVACMode.COOL if self.coordinator.data.get("climate_on") else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode):
        await self.coordinator.api.set_climate(hvac_mode == HVACMode.COOL)
        await self.coordinator.async_request_refresh()