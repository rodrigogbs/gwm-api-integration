from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalLockSwitch(coordinator)])

class HavalLockSwitch(SwitchEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Haval Trava"

    @property
    def is_on(self):
        return self.coordinator.data.get("doors_locked")

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_lock(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_lock(False)