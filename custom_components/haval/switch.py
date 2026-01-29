
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalLockSwitch(coord)])

class HavalLockSwitch(CoordinatorEntity, SwitchEntity):
    @property
    def is_on(self):
        return self.coordinator.data.get("doors_locked")

    async def async_turn_on(self):
        await self.coordinator.api.lock_doors(True)
        await self.coordinator.async_refresh()

    async def async_turn_off(self):
        await self.coordinator.api.lock_doors(False)
        await self.coordinator.async_refresh()
