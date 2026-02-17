"""Config flow for adaptive_control integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_CONTROL_REGULARIZATION,
    CONF_INPUT_SENSOR,
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_OUTPUT_ENTITY,
    CONF_RLS_FORGETTING,
    CONF_TARGET,
    DEFAULT_CONTROL_REGULARIZATION,
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    DEFAULT_RLS_FORGETTING,
    DEFAULT_TARGET,
    DOMAIN,
)


class AdaptiveControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for adaptive_control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_INPUT_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor"),
                    ),
                    vol.Required(CONF_OUTPUT_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["number", "input_number"]
                        ),
                    ),
                    vol.Optional(CONF_TARGET, default=DEFAULT_TARGET): vol.Coerce(
                        float
                    ),
                    vol.Optional(CONF_MIN_VALUE, default=DEFAULT_MIN_VALUE): vol.Coerce(
                        float
                    ),
                    vol.Optional(CONF_MAX_VALUE, default=DEFAULT_MAX_VALUE): vol.Coerce(
                        float
                    ),
                    vol.Optional(
                        CONF_RLS_FORGETTING, default=DEFAULT_RLS_FORGETTING
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
                    vol.Optional(
                        CONF_CONTROL_REGULARIZATION,
                        default=DEFAULT_CONTROL_REGULARIZATION,
                    ): vol.Coerce(float),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return AdaptiveControlOptionsFlowHandler(config_entry)


class AdaptiveControlOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for adaptive_control."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_INPUT_SENSOR,
                        default=self.config_entry.options.get(
                            CONF_INPUT_SENSOR,
                            self.config_entry.data.get(CONF_INPUT_SENSOR),
                        ),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor"),
                    ),
                    vol.Optional(
                        CONF_OUTPUT_ENTITY,
                        default=self.config_entry.options.get(
                            CONF_OUTPUT_ENTITY,
                            self.config_entry.data.get(CONF_OUTPUT_ENTITY),
                        ),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["number", "input_number"]
                        ),
                    ),
                    vol.Optional(
                        CONF_TARGET,
                        default=self.config_entry.options.get(
                            CONF_TARGET,
                            self.config_entry.data.get(CONF_TARGET, DEFAULT_TARGET),
                        ),
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_MIN_VALUE,
                        default=self.config_entry.options.get(
                            CONF_MIN_VALUE,
                            self.config_entry.data.get(
                                CONF_MIN_VALUE, DEFAULT_MIN_VALUE
                            ),
                        ),
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_MAX_VALUE,
                        default=self.config_entry.options.get(
                            CONF_MAX_VALUE,
                            self.config_entry.data.get(
                                CONF_MAX_VALUE, DEFAULT_MAX_VALUE
                            ),
                        ),
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_RLS_FORGETTING,
                        default=self.config_entry.options.get(
                            CONF_RLS_FORGETTING,
                            self.config_entry.data.get(
                                CONF_RLS_FORGETTING, DEFAULT_RLS_FORGETTING
                            ),
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
                    vol.Optional(
                        CONF_CONTROL_REGULARIZATION,
                        default=self.config_entry.options.get(
                            CONF_CONTROL_REGULARIZATION,
                            self.config_entry.data.get(
                                CONF_CONTROL_REGULARIZATION,
                                DEFAULT_CONTROL_REGULARIZATION,
                            ),
                        ),
                    ): vol.Coerce(float),
                }
            ),
        )
