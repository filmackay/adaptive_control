"""Switch platform for adaptive_control."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .coordinator import AdaptiveControlCoordinator
from .data import AdaptiveControlConfigEntry
from .entity import AdaptiveControlEntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: AdaptiveControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([AdaptiveControlEnableSwitch(coordinator)])


class AdaptiveControlEnableSwitch(AdaptiveControlEntity, SwitchEntity, RestoreEntity):
    """Switch to enable/disable the adaptive control loop."""

    _attr_icon = "mdi:power"

    def __init__(self, coordinator: AdaptiveControlCoordinator):
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.config_entry.title} Enable"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_enable"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self._is_on

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        self._is_on = True
        self.coordinator.set_enabled(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        self._is_on = False
        self.coordinator.set_enabled(False)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state == "on":
            self._is_on = True
            self.coordinator.set_enabled(True)
        else:
            self._is_on = False
            self.coordinator.set_enabled(False)
