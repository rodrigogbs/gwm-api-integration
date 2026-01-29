
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .api import HavalApi
from homeassistant.helpers.aiohttp_client import async_get_clientsession

class HavalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            try:
                api = HavalApi(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    async_get_clientsession(self.hass)
                )
                await api.authenticate()
                return self.async_create_entry(
                    title="Haval Vehicle",
                    data=user_input
                )
            except Exception:
                errors["base"] = "auth_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
