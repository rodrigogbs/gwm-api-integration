
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data["haval"][entry.entry_id]
    async_add_entities([HavalClimate(coord)])

class HavalClimate(CoordinatorEntity, ClimateEntity):
    @property
    def hvac_mode(self):
        return HVACMode.COOL if self.coordinator.data.get("climate") else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode):
        await self.coordinator.api.set_climate(hvac_mode != HVACMode.OFF)
        await self.coordinator.async_refresh()
