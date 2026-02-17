"""AdaptiveControlEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AdaptiveControlCoordinator


class AdaptiveControlEntity(CoordinatorEntity[AdaptiveControlCoordinator]):
    """AdaptiveControlEntity class."""

    def __init__(self, coordinator: AdaptiveControlCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer="Custom Integration",
        )
