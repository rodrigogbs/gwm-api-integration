from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD

class HavalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="Haval Vehicle", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            })
        )