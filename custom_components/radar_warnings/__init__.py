"""The radar_warnings component."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS
from .coordinator import RadarWarningsConfigEntry, RadarWarningsCoordinator



async def async_setup_entry(hass: HomeAssistant, entry: RadarWarningsConfigEntry) -> bool:
    """Set up a config entry."""
    coordinator = RadarWarningsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: RadarWarningsConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: RadarWarningsConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)
