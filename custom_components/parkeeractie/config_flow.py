from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ParkeeractieClient
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # Proeflogin
            session = async_get_clientsession(self.hass)
            client = ParkeeractieClient(
                session, user_input["username"], user_input["password"]
            )
            try:
                await client.login_and_fetch()
                return self.async_create_entry(title="Parkeeractie", data=user_input)
            except Exception as e:
                msg = str(e)
                if "reCAPTCHA" in msg or "showCaptcha" in msg:
                    errors["base"] = "captcha_required"
                else:
                    errors["base"] = "auth"

        schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
