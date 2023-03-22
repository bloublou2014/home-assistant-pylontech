"""Config flow to configure Pylontech BMS integration."""
from __future__ import annotations

from typing import Any

import logging
import voluptuous as vol

from .pylontech import PylontechBMS

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DEFAULT_NAME,
    DOMAIN,
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="pylontech.local"): str,
        vol.Required(CONF_PORT, default=1234): int,
    }
)

_LOGGER = logging.getLogger(__name__)


class PylontechFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Pylontech BMS config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            try:
                pylontech = PylontechBMS(host, port)
                await pylontech.connect()
                info = await pylontech.info()
                await pylontech.disconnect()
            except Exception:
                errors["base"] = "connection_error"
            else:
                await self.async_set_unique_id(info.module_barcode.value)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )
