from __future__ import annotations

import uuid
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HavalApi
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_DEVICE_ID, CONF_COMMAND_PASSWORD
from .exceptions import HavalAuthError


class HavalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input:
            device_id = str(uuid.uuid4())

            api = HavalApi(
                session=async_get_clientsession(self.hass),
                username=user_input[CONF_USERNAME],
                password_plain=user_input[CONF_PASSWORD],
                device_id=device_id,
            )

            try:
                await api.login()
                vin = await api.acquire_vehicles()
            except HavalAuthError:
                errors["base"] = "auth_failed"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                # Store command password too (optional)
                return self.async_create_entry(
                    title=f"Haval {vin}",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_DEVICE_ID: device_id,
                        CONF_COMMAND_PASSWORD: user_input.get(CONF_COMMAND_PASSWORD, ""),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_COMMAND_PASSWORD, default=""): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
