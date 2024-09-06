"""Support for getting radar warning data from atudo.

Data is fetched from atudo:
https://cdn2.atudo.net
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE

from .const import (
    RADAR_WARNING_SENSOR,
    DOMAIN,
    ATTR_LAST_UPDATE,
    ATTR_WARNING_COUNT,
    API_ATTR_WARNING_ID, 
    API_ATTR_WARNING_DISTANCE, 
    API_ATTR_WARNING_STREET, 
    API_ATTR_WARNING_VMAX,
    LOGGER
)


from .coordinator import RadarWarningsConfigEntry,RadarWarningsCoordinator

SENSOR_TYPE: SensorEntityDescription = (
    SensorEntityDescription(
        key=RADAR_WARNING_SENSOR,
        translation_key=RADAR_WARNING_SENSOR,
    )
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: RadarWarningsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entities from config entry."""
    coordinator = entry.runtime_data

    unique_id = entry.unique_id
    assert unique_id

    async_add_entities(
        [RadarWarningsSensor(coordinator, SENSOR_TYPE, unique_id)]
    )


class RadarWarningsSensor(
    CoordinatorEntity[RadarWarningsCoordinator], SensorEntity
):
    """Representation of a Radar Warnings sensor."""

    _attr_attribution = "Data provided by Radar warnings"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RadarWarningsCoordinator,
        description: SensorEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize a Radar Warnings sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{unique_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name="Radar Warnings",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.api.__len__()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        data = {
            ATTR_LAST_UPDATE: self.coordinator.api.last_update,
            ATTR_WARNING_COUNT: self.coordinator.api.__len__()
        }

        pois = self.coordinator.api.pois
        data[f"warnings"] = pois.copy()
        for i, poi in enumerate(pois, 1):
            data[f"warning_{i}_id"] = poi[API_ATTR_WARNING_ID]
            data[f"warning_{i}_latitude"] = poi[ATTR_LATITUDE]
            data[f"warning_{i}_longitude"] = poi[ATTR_LONGITUDE]
            data[f"warning_{i}_street"] = poi[API_ATTR_WARNING_STREET]
            data[f"warning_{i}_vmax"] = poi[API_ATTR_WARNING_VMAX]
            data[f"warning_{i}_distance"] = poi[API_ATTR_WARNING_DISTANCE]

        return data

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self.coordinator.api.last_update is not None
