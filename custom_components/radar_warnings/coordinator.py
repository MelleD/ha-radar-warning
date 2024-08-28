"""Data coordinator for the radar_warnings integration."""

from __future__ import annotations

from .radar_api import RadarWarningApi

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from datetime import timedelta

from .const import (
    DOMAIN,
    LOGGER,
)

from homeassistant.const import (
    CONF_RADIUS,
    CONF_LATITUDE, 
    CONF_LONGITUDE
)


type RadarWarningsConfigEntry = ConfigEntry[RadarWarningsCoordinator]

class RadarWarningsCoordinator(DataUpdateCoordinator[None]):
    """Custom coordinator for the radar_warnings integration."""

    config_entry: RadarWarningsConfigEntry

    def __init__(self, hass: HomeAssistant, entry: RadarWarningsConfigEntry, scan_interval: timedelta) -> None:
        """Initialize the radar_warnings coordinator."""
        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=scan_interval
        )
        self.config_entry = entry

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh."""
        self._latitude = self.config_entry.data.get(CONF_LATITUDE, 0)
        self._longitude = self.config_entry.data.get(CONF_LONGITUDE, 0)
        self._radius = self.config_entry.data.get(CONF_RADIUS, 10.0)
        self.api = RadarWarningApi(self._latitude, self._longitude, self._radius)

        await self._async_update_data()
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> None:
        """Get the latest data from the Radar Warnings API."""
        await self.hass.async_add_executor_job(self.api.update_pois)
