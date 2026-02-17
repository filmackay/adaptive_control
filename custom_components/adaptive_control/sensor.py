"""Sensor platform for adaptive_control."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import AdaptiveControlCoordinator
from .data import AdaptiveControlConfigEntry
from .entity import AdaptiveControlEntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: AdaptiveControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    entities = [
        AdaptiveControlOutputSensor(coordinator, entry),
        AdaptiveControlMetricSensor(
            coordinator,
            entry,
            key="system_gain",
            name="System Gain",
            icon="mdi:arrow-up-bold-box-outline",
        ),
        AdaptiveControlMetricSensor(
            coordinator,
            entry,
            key="prediction_error",
            name="Prediction Error",
            icon="mdi:alert-circle-outline",
        ),
        AdaptiveControlMetricSensor(
            coordinator, entry, key="cost", name="Cost Function", icon="mdi:chart-line"
        ),
    ]
    async_add_entities(entities)


class AdaptiveControlOutputSensor(AdaptiveControlEntity, SensorEntity):
    """Main Control Output Sensor."""

    _attr_icon = "mdi:flash-auto"
    _attr_state_class = SensorStateClass.MEASUREMENT
    # Unit should ideally match the controlled entity, but we don't know it easily yet.
    # For now, no unit or maybe "A" if we assume Amps? Let's leave it blank or copies from input?
    # Actually, the user can customize it in UI.

    def __init__(
        self,
        coordinator: AdaptiveControlCoordinator,
        config_entry: AdaptiveControlConfigEntry,
    ):
        super().__init__(coordinator)
        self._attr_name = f"{config_entry.title} Output"
        self._attr_unique_id = f"{config_entry.entry_id}_output"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("output")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return metrics as attributes."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("metrics", {})


class AdaptiveControlMetricSensor(AdaptiveControlEntity, SensorEntity):
    """Diagnostic Metric Sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, config_entry, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{config_entry.title} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        metrics = self.coordinator.data.get("metrics", {})
        return metrics.get(self._key)
