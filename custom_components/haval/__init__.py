from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .api import HavalAPI
from .coordinator import HavalCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = HavalAPI(
        entry.data["email"],
        entry.data["password"]
    )

    await api.login()

    coordinator = HavalCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
