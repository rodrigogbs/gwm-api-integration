from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_COMMAND_PASSWORD
from .util import get_first


async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    cmd_pwd = entry.data.get(CONF_COMMAND_PASSWORD, "")
    async_add_entities([HavalClimate(coord, cmd_pwd)])


class HavalClimate(CoordinatorEntity, ClimateEntity):
    _attr_name = "Haval Ar-Condicionado"
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL]

    def __init__(self, coordinator, command_password: str):
        super().__init__(coordinator)
        vin = getattr(coordinator, "vin", None) or "unknown"
        self._vin = vin
        self._cmd_pwd = command_password or ""
        self._attr_unique_id = f"{vin}_climate"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vin)},
            "manufacturer": "GWM",
            "model": "Haval",
            "name": f"Haval {vin}",
        }

    @property
    def available(self):
        # If user didn't provide command password, treat controls as unavailable (read-only)
        return super().available and bool(self._cmd_pwd)

    @property
    def hvac_mode(self):
        # Best-effort: infer from any known field
        enabled = get_first(self.coordinator.data, ["climate_on", "airConditionStatus", "airConditioner.switch", "vehicleStatus.airConditionStatus"], default=False)
        return HVACMode.COOL if bool(enabled) else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode):
        enable = hvac_mode != HVACMode.OFF
        await self.coordinator.api.send_cmd_ac(vin=self._vin, command_password_plain=self._cmd_pwd, enable=enable, temperature_c=18)
        await self.coordinator.async_request_refresh()
