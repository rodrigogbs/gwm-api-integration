from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HavalLockSwitch(coordinator)])

class HavalLockSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Haval Trava"
        self._attr_unique_id = f"{coordinator.data['vin']}_lock"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.data["vin"])},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": "Haval Vehicle",
        }

    @property
    def is_on(self):
        return self.coordinator.data.get("doors_locked")

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_lock(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_lock(False)
        await self.coordinator.async_request_refresh()