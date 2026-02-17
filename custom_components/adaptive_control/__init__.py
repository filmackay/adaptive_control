"""Custom integration to integrate adaptive_control with Home Assistant.

For more details about this integration, please refer to
https://github.com/filmackay/adaptive_control
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN, LOGGER
from .coordinator import AdaptiveControlCoordinator
from .data import AdaptiveControlData

__all__ = [
    "DOMAIN",
    "LOGGER",
    "AdaptiveControlCoordinator",
    "AdaptiveControlData",
    "async_get_loaded_integration",
]

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AdaptiveControlConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdaptiveControlConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = AdaptiveControlCoordinator(
        hass=hass,
        config_entry=entry,
    )
    # Create Controller Instance inside Coordinator (or passed to it)

    entry.runtime_data = AdaptiveControlData(
        controller=coordinator.controller,
        # integration=async_get_loaded_integration(hass, entry.domain),
        integration=None,  # Not really needed here
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: AdaptiveControlConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: AdaptiveControlConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
