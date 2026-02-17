"""Number platform for adaptive_control."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up the number platform."""
    coordinator = entry.runtime_data.coordinator

    # We use coordinator values as defaults since coordinator already loaded them from config
    async_add_entities(
        [
            AdaptiveControlNumber(
                coordinator,
                key="target",
                name="Target",
                icon="mdi:target",
                default=coordinator.target,
                min_val=-10000,
                max_val=10000,
                step=1,
            ),
            AdaptiveControlNumber(
                coordinator,
                key="min",
                name="Minimum Output",
                icon="mdi:arrow-down-bold-box-outline",
                default=coordinator.min_val,
                min_val=0,
                max_val=10000,
                step=1,
            ),
            AdaptiveControlNumber(
                coordinator,
                key="max",
                name="Maximum Output",
                icon="mdi:arrow-up-bold-box-outline",
                default=coordinator.max_val,
                min_val=0,
                max_val=10000,
                step=1,
            ),
        ]
    )


class AdaptiveControlNumber(AdaptiveControlEntity, NumberEntity, RestoreEntity):
    """Number entity for setting parameters."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: AdaptiveControlCoordinator,
        key: str,
        name: str,
        icon: str,
        default: float,
        min_val: float,
        max_val: float,
        step: float,
    ):
        super().__init__(coordinator)
        self.coordinator = coordinator  # Type hint
        self._key = key
        self._attr_name = f"{coordinator.config_entry.title} {name}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"
        self._attr_icon = icon
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._default = default
        self._attr_native_value = default

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        if self._key == "target":
            self.coordinator.set_target(value)
        elif self._key == "min":
            self.coordinator.set_min(value)
        elif self._key == "max":
            self.coordinator.set_max(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ("unknown", "unavailable"):
            try:
                val = float(last_state.state)
                # Check for nan
                if val != val:
                    val = self._default
                self._attr_native_value = val
                # Update coordinator immediately on restore
                await self.async_set_native_value(val)
            except ValueError:
                self._attr_native_value = self._default
                await self.async_set_native_value(self._default)
        else:
            # First run, sync coordinator with default (from config)
            self._attr_native_value = self._default
            await self.async_set_native_value(self._default)
