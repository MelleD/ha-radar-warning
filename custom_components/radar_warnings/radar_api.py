import json
import math
import aiohttp
import asyncio
import socket

from geopy.distance import geodesic
from geopy.point import Point
from datetime import UTC, datetime

from .exceptions import RadarWarningConnectionError

from .const import LOGGER, API_ATTR_WARNING_ID, API_ATTR_WARNING_DISTANCE, API_ATTR_WARNING_STREET, API_ATTR_WARNING_VMAX
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE


class POI:
    def __init__(self, id, latitude, longitude, street, vmax, distance):
        self.id = id
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.street = street
        self.vmax = vmax
        self.distance = distance

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
    
    def to_json(self):
        return {
            API_ATTR_WARNING_ID: self.id,
            ATTR_LATITUDE: self.latitude,
            ATTR_LONGITUDE: self.longitude,
            API_ATTR_WARNING_STREET: self.street,
            API_ATTR_WARNING_VMAX: self.vmax,
            API_ATTR_WARNING_DISTANCE: self.distance
        }

    def __repr__(self):
        return f"{self.to_json()}"

class RadarWarningApi:

    def __init__(self,latitude: float, longitude: float, radius_km: float, session: aiohttp.client.ClientSession | None = None):
        self.latitude = latitude
        self.longitude = longitude 
        self.radius_km = radius_km
        self.last_update = None
        self._session = session
        self._close_session = False


    def __len__(self):
        """Return the count of pois."""
        return len(self.pois)

    def get_coordinates(self, grad: int):
        abstand = math.sqrt(self.radius_km*self.radius_km + self.radius_km*self.radius_km) * 1000  # Angabe in Meter!
        
        # Wegpunktprojektion berechnen
        dnord = (math.cos(math.radians(grad)) * abstand) / 1850  # Ergebnis in Grad
        dost = (math.sin(math.radians(grad)) * abstand) / (1850 * math.cos(math.radians(self.latitude)))
        new_lat = self.latitude + dnord / 60
        new_lng = self.longitude + dost / 60
        
        return new_lat, new_lng

    def get_url(self):
        get_type = "0,1,2,3,4,5,6"
        area_top_right_coordinates = self.get_coordinates(45)
        area_top_right_latitude=area_top_right_coordinates[0]
        area_top_right_longitude=area_top_right_coordinates[1]
        area_top_left_coordinates = self.get_coordinates(225)
        area_top_left_latitude=area_top_left_coordinates[0]
        area_top_left_longitude=area_top_left_coordinates[1]

        return f"https://cdn2.atudo.net/api/1.0/vl.php?type={get_type}&box={area_top_left_latitude},{area_top_left_longitude},{area_top_right_latitude},{area_top_right_longitude}"

    async def get_pois(self):
        url = self.get_url()
        http_timeout = 5
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(http_timeout):
                response = await self._session.get(url)
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to Radar warnings instance."
            raise RadarWarningConnectionError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with Radar warnings instance."
            raise RadarWarningConnectionError(msg) from exception
        
        if response.status // 100 in [4, 5]:
            contents = await response.read()
            response.close()
            raise RadarWarningConnectionError(
                response.status, json.loads(contents.decode("utf8"))
            )

        data = await response.json()
        pois = list()

        # Durch die pois iterieren und das info-Feld als Dictionary parsen
        for poi in data['pois']:
            poi['info'] = json.loads(poi['info'])

        # Datenstruktur ausgeben
        for poi_data in data['pois']:
            start_point = Point(self.latitude, self.longitude)
            end_point = Point(poi_data['lat'], poi_data['lng'])
            distance = geodesic(start_point, end_point).kilometers
            if distance <= self.radius_km:
                poi = POI(
                    id=poi_data['id'],
                    latitude=poi_data['lat'],
                    longitude=poi_data['lng'],
                    street=poi_data.get('street', ""),
                    vmax=poi_data['vmax'],
                    distance=distance
                ).to_json()
                pois.append(poi)
        return pois

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def update_pois(self):
        LOGGER.debug("start poi update")
        self.last_update = None
        pois = await self.get_pois()
        self.pois = pois
        for poi in self.pois:
            LOGGER.debug(poi)

        await self.close()
        self.last_update = datetime.now(UTC)
