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
from homeassistant.const import UnitOfLength
from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers import device_registry as dr

from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE

from .const import (
    RADAR_WARNING_SENSOR,
    DOMAIN,
    ATTR_LAST_UPDATE,
    ATTR_WARNING_COUNT,
    API_ATTR_WARNING_DISTANCE, 
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
            lambda now: self._update(),
            self._coordinator.update_interval,
            cancel_on_shutdown=True,
        )

    def _remove_entity(self) -> None:
        device_reg = dr.async_get(self._hass)
        LOGGER.warn("Remove device1:")
        device1 = device_reg.async_get_device("zoo_1")
        self._hass.add_job(device1.async_remove())
        device2 = device_reg.async_get_device("zoo_2")
        self._hass.add_job(device2.async_remove())
        LOGGER.warn("Removed devices:")
        max_iterations=1000
        for i in range(1,max_iterations):
            unique_id_radar = self._radar_map_name(i)
            LOGGER.warn("Remove device: %s", unique_id_radar)
            device = device_reg.async_get_device(unique_id_radar)
            LOGGER.warn("Remove Found device: %s", device)
            if device is None:
                return
            self._hass.add_job(device.async_remove())

    async def _update(self) -> None:
        """Update Map entry."""
        LOGGER.warn("Update Map entry, devices to update: %d", len(self._managed_devices))
        self._remove_entity()

        #for device in list(self._managed_devices):
        #    LOGGER.warn("Remove device 2")
        #    self._managed_devices.remove(device)
        #    self._hass.add_job(device.async_remove())

        pois = self._coordinator.api.pois
        for i, poi in enumerate(pois, 1):
            unique_id_radar = self._radar_map_name(i)
            LOGGER.warn("New device: %s", unique_id_radar)
            new_device = RadarMapWarningsSensor(unique_id_radar,poi[API_ATTR_WARNING_DISTANCE],poi[ATTR_LATITUDE],poi[ATTR_LONGITUDE])  
            self._managed_devices.append(new_device)    
        await self._add_entities(self._managed_devices)
        LOGGER.warn("Added New device")
    
    def _radar_map_name(self, count: int) -> str:
         """Radar Map Sensor name."""
         return f"{DOMAIN}_{self._unique_id}_{count}"


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

class RadarMapWarningsSensor(GeolocationEvent):
    """Representation of a Radar Warnings sensor."""

    _attr_attribution = "Data provided by Radar warnings"
    _attr_should_poll = False

    def __init__(
        self,
        name: str,
        distance: float,
        latitude: float,
        longitude: float
    ) -> None:
        """Initialize entity with data provided."""
        self._attr_name = name
        self._attr_icon = "mdi:cctv"
        self._distance = distance
        self._latitude = latitude
        self._longitude = longitude
        self._unit_of_measurement = UnitOfLength.KILOMETERS
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, name)},
            name="Radar Warnings",
            entry_type=DeviceEntryType.SERVICE,
        )



    @property
    def source(self) -> str:
        """Return source value of this external event."""
        return DOMAIN

    @property
    def distance(self) -> float | None:
        """Return distance value of this external event."""
        return self._distance

    @property
    def latitude(self) -> float | None:
        """Return latitude value of this external event."""
        return self._latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude value of this external event."""
        return self._longitude

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement