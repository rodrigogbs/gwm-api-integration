from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalClimate(coordinator)])

class HavalClimate(ClimateEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Haval Ar"

    @property
    def hvac_mode(self):
        return HVACMode.COOL if self.coordinator.data.get("climate_on") else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode):
        await self.coordinator.api.set_climate(hvac_mode == HVACMode.COOL)