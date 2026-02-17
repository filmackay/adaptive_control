"""DataUpdateCoordinator for adaptive_control."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .adaptive_logic import AdaptiveFIRController
from .const import (
    CONF_INPUT_SENSOR,
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_OUTPUT_ENTITY,
    CONF_TARGET,
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    DEFAULT_TARGET,
    DOMAIN,
    LOGGER,
)

if TYPE_CHECKING:
    from .data import AdaptiveControlConfigEntry


class AdaptiveControlCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: AdaptiveControlConfigEntry
    controller: AdaptiveFIRController

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: AdaptiveControlConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=None,  # Event driven
        )
        self.config_entry = config_entry
        self.controller = AdaptiveFIRController()

        # Load params (or defaults)
        self.input_sensor = config_entry.data.get(CONF_INPUT_SENSOR)
        self.output_entity = config_entry.data.get(CONF_OUTPUT_ENTITY)
        self.target = config_entry.options.get(
            CONF_TARGET, config_entry.data.get(CONF_TARGET, DEFAULT_TARGET)
        )
        self.min_val = config_entry.options.get(
            CONF_MIN_VALUE, config_entry.data.get(CONF_MIN_VALUE, DEFAULT_MIN_VALUE)
        )
        self.max_val = config_entry.options.get(
            CONF_MAX_VALUE, config_entry.data.get(CONF_MAX_VALUE, DEFAULT_MAX_VALUE)
        )

        self.enabled = False  # controlled by switch entity

        # Subscribe to input sensor changes
        if self.input_sensor:
            self.cancel_listen = async_track_state_change_event(
                hass, [self.input_sensor], self._async_handle_event
            )

    async def _async_update_data(self) -> Any:
        """Update data via polling (not used primarily)."""
        # This is called if request_refresh is manually called
        return self._run_control_loop()

    def set_enabled(self, enabled: bool):
        """Enable or disable the control loop."""
        self.enabled = enabled
        self._run_control_loop()

    def set_target(self, value: float):
        """Update target value."""
        self.target = value

    def set_min(self, value: float):
        """Update min value."""
        self.min_val = value

    def set_max(self, value: float):
        """Update max value."""
        self.max_val = value

    @callback
    def _async_handle_event(self, _event):
        """Handle input sensor state change."""
        if not self.enabled:
            return
        self.async_set_updated_data(self._run_control_loop())

    def _run_control_loop(self) -> dict[str, Any]:
        """Run the adaptive control logic."""
        hass = self.hass

        # Get Measured Value
        measured_state = hass.states.get(self.input_sensor)
        if not measured_state or measured_state.state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            return {}

        try:
            measured = float(measured_state.state)
        except ValueError:
            return {}

        # Get Reflected Control (What the device is currently doing)
        control_state = hass.states.get(self.output_entity)
        if control_state and control_state.state not in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            try:
                control = int(float(control_state.state))
            except ValueError:
                control = 0
        else:
            control = 0  # Assume 0 if unknown

        # Constants from options (allow runtime update)
        target = self.config_entry.options.get(CONF_TARGET, self.target)
        min_val = self.config_entry.options.get(CONF_MIN_VALUE, self.min_val)
        max_val = self.config_entry.options.get(CONF_MAX_VALUE, self.max_val)

        # Run Update
        output, metrics = self.controller.update(
            target=target,
            measured=measured,
            control=control,
            min_out=int(min_val),
            max_out=int(max_val),
        )

        return {
            "output": output,
            "metrics": metrics,
            "target": target,
            "min": min_val,
            "max": max_val,
        }
