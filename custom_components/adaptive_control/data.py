"""Custom types for adaptive_control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .adaptive_logic import AdaptiveFIRController
    from .coordinator import AdaptiveControlCoordinator


type AdaptiveControlConfigEntry = ConfigEntry[AdaptiveControlData]


@dataclass
class AdaptiveControlData:
    """Data for the Adaptive Control integration."""

    controller: AdaptiveFIRController
    coordinator: AdaptiveControlCoordinator
    integration: Integration
