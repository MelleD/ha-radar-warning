"""Constants for the radar_warning integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)

DOMAIN: Final = "radar_warning_warnings"

CONF_ZONE_ENTITY: Final = "zone_entity"

ATTR_LAST_UPDATE: Final = "last_update"
ATTR_WARNING_COUNT: Final = "warning_count"

API_ATTR_WARNING_STREET: Final = "street"
API_ATTR_WARNING_VMAX: Final = "vmax"

DEFAULT_NAME: Final = "Radar Warnings"
DEFAULT_SCAN_INTERVAL: Final = timedelta(minutes=60)

RADAR_WARNING_SENSOR: Final = "radar_warning"

PLATFORMS: Final[list[Platform]] = [Platform.SENSOR]
