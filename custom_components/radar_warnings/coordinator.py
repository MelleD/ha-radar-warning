"""Data coordinator for the radar_warnings integration."""

from __future__ import annotations

from .radar_api import RadarWarningApi

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_ZONE_ENTITY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)

from homeassistant.const import (
    CONF_RADIUS
)

from .util import get_zone_position_data

type RadarWarningsConfigEntry = ConfigEntry[RadarWarningsCoordinator]


class RadarWarningsCoordinator(DataUpdateCoordinator[None]):
    """Custom coordinator for the radar_warnings integration."""

    config_entry: RadarWarningsConfigEntry
    api: RadarWarningApi
    _zone_entity: str
    _radius: float

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the radar_warnings coordinator."""
        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )

        self._zone_entity = ""
        self._radius = 10

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh."""
        self._zone_entity = self.config_entry.data.get(CONF_ZONE_ENTITY, "")
        self._radius = self.config_entry.data.get(CONF_RADIUS, 10)
        position = get_zone_position_data(self.hass, self._zone_entity)
        self.api = RadarWarningApi(position[0], position[1], self._radius)

        await self._async_update_data()
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> None:
        """Get the latest data from the Radar Warnings API."""
        await self.hass.async_add_executor_job(self.api.update_pois)
