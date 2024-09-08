"""Support for getting radar warning data from atudo.

Data is fetched from atudo:
https://cdn2.atudo.net
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import DOMAIN as SENSOR_PLATFORM
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfLength
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers import entity_registry as er

from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, ATTR_ICON, ATTR_UNIT_OF_MEASUREMENT
from datetime import datetime

from .const import (
    RADAR_WARNING_SENSOR,
    DOMAIN,
    ATTR_LAST_UPDATE,
    ATTR_WARNING_COUNT,
    API_ATTR_WARNING_DISTANCE,
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
    if coordinator.show_map is True:
        MapManager(hass, coordinator, unique_id, async_add_entities)

class MapManager:
    """Device manager for geolocation events."""

    def __init__(self, hass: HomeAssistant ,coordinator: RadarWarningsCoordinator,unique_id:str, add_entities: AddEntitiesCallback) -> None:
        """Initialise the demo geolocation event manager."""
        self._hass = hass
        self._coordinator = coordinator
        self._add_entities = add_entities
        self._managed_devices: list[RadarMapWarningsSensor] = []
        self._unique_id = unique_id
        self._update()
        self._init_regular_updates()

    def _init_regular_updates(self) -> None:
        """Schedule regular updates based on configured time interval."""
        async_track_time_interval(
            self._hass,
            self._update_async_track_time_interval,
            self._coordinator.update_interval,
            cancel_on_shutdown=True,
        )

    @callback
    def _update_async_track_time_interval(self, now: datetime | None = None) -> None:
        """Async update"""
        self._update()

    def _remove_entity(self) -> None:
        entity_reg = er.async_get(self._hass)
        start =  len(self._managed_devices) + 1
        for device in list(self._managed_devices):
            self._managed_devices.remove(device)
            self._hass.add_job(device.async_remove())
           

        max_iterations=1000
        for i in range(start,max_iterations):
            unique_id_radar = self._radar_map_name(i)
            entity = entity_reg.async_get_entity_id(SENSOR_PLATFORM, DOMAIN, unique_id_radar)
            LOGGER.warn("Entity found: %s", entity)
            if entity_id := entity_reg.async_get_entity_id(SENSOR_PLATFORM, DOMAIN, unique_id_radar):
                entity_reg.async_remove(entity_id)


    def _update(self) -> None:
        """Update Map entry."""
        self._remove_entity()

        pois = self._coordinator.api.pois
        for i, poi in enumerate(pois, 1):
            unique_id_radar = self._radar_map_name(i)
            LOGGER.warn("New device: %s", unique_id_radar)
            new_device = RadarMapWarningsSensor(unique_id_radar,poi[API_ATTR_WARNING_DISTANCE],poi[ATTR_LATITUDE],poi[ATTR_LONGITUDE])  
            self._managed_devices.append(new_device)    
        self._add_entities(self._managed_devices)
        LOGGER.warn("Added New device")
    
    def _radar_map_name(self, count: int) -> str:
         """Radar Map Sensor name."""
         return f"{self._unique_id}_{count}"


class RadarWarningsSensor(
    CoordinatorEntity[RadarWarningsCoordinator], SensorEntity
):
    """Representation of a Radar Warnings sensor."""

    _attr_attribution = "Data provided by Radar warnings"

    def __init__(
        self,
        coordinator: RadarWarningsCoordinator,
        description: SensorEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize a Radar Warnings sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = unique_id
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

        return data

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self.coordinator.api.last_update is not None

class RadarMapWarningsSensor(SensorEntity):
    """Representation of a Radar Warnings sensor."""

    _attr_attribution = "Data provided by Radar warnings"
    _attr_should_poll = False

    def __init__(
        self,
        unique_id: str,
        distance: float,
        latitude: float,
        longitude: float
    ) -> None:
        """Initialize entity with data provided."""
        self._attr_unique_id = unique_id
        self._attr_icon = "mdi:cctv"
        self._distance = distance
        self._latitude = latitude
        self._longitude = longitude
        self._unit_of_measurement = UnitOfLength.KILOMETERS
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name="Radar Warnings",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self._distance

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        data = {
            ATTR_LATITUDE: self._latitude,
            ATTR_LONGITUDE: self._longitude,
            ATTR_UNIT_OF_MEASUREMENT: self._unit_of_measurement,
            ATTR_ICON: self._attr_icon
        }

        return data

    @property
    def source(self) -> str:
        """Return source value of this external event."""
        return DOMAIN