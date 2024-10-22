import json
import math
import aiohttp
import asyncio
import socket

from geopy.distance import geodesic
from geopy.point import Point
from datetime import UTC, datetime

from .exceptions import RadarWarningConnectionError

from .const import LOGGER, API_ATTR_WARNING_ID, API_ATTR_WARNING_DISTANCE, API_ATTR_WARNING_STREET, API_ATTR_WARNING_VMAX, API_ATTR_WARNING_ADRESS, API_ATTR_WARNING_ADRESS_SHORT,API_ATTR_WARNING_CITY
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE


class POI:
    def __init__(self, id, latitude, longitude, street, vmax, distance, adress: str | None = None, adress_short: str | None = None, city: str | None = None):
        self.id = id
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.street = street
        self.vmax = vmax
        self.distance = distance
        self.adress = adress
        self.adress_short= adress_short
        self.city = city

    def __eq__(self, other):
        if isinstance(other, POI):
            id_equal = self.id == other.id
            lat_equal = abs(self.latitude - other.latitude) < 1e-6
            lon_equal = abs(self.longitude - other.longitude) < 1e-6
            return id_equal or (lat_equal and lon_equal)
        return False

    def __hash__(self):
        # Hash basierend auf ID, Latitude und Longitude
        return hash((self.id, self.latitude, self.longitude))

    
    def to_json(self):
        return {
            API_ATTR_WARNING_ID: self.id,
            ATTR_LATITUDE: self.latitude,
            ATTR_LONGITUDE: self.longitude,
            API_ATTR_WARNING_STREET: self.street,
            API_ATTR_WARNING_VMAX: self.vmax,
            API_ATTR_WARNING_DISTANCE: self.distance,
            API_ATTR_WARNING_ADRESS: self.adress,
            API_ATTR_WARNING_ADRESS_SHORT: self.adress_short,
            API_ATTR_WARNING_CITY: self.city
        }

    def __repr__(self):
        return f"{self.to_json()}"

class RadarWarningApi:

    def __init__(self,latitude: float, longitude: float, radius_km: float, session: aiohttp.client.ClientSession | None = None, google_api_key: str | None = None):
        self.latitude = latitude
        self.longitude = longitude 
        self.radius_km = radius_km
        self.last_update = None
        self._session = session
        self._close_session = False
        self.google_api_key = google_api_key
        
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
    
    def get_google_url(self, point: Point):
        return f"https://maps.googleapis.com/maps/api/geocode/json?latlng={point.latitude},{point.longitude}&key={self.google_api_key}"

    async def get_adress(self, point: Point, street: str | None) -> tuple[str | None, str | None, str | None, str | None]:
        if self.google_api_key is None:
            return (street, street, street, None)
    
        url = self.get_google_url(point)
        http_timeout = 15
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
            raise RadarWarningConnectionError("HTTP error occurred",
                response.status, json.loads(contents.decode("utf8"))
            )

        data_adress = await response.json()
        if 'results' in data_adress and len(data_adress['results']) > 0:
            first_result = data_adress['results'][0]
            formatted_address = first_result['formatted_address']
            address_components = first_result['address_components']
            
            city = "unknown"
            for component in address_components:
                if 'locality' in component['types']:
                    city = component['long_name']

                if 'route' in component['types'] and street is None:
                    street = component['long_name']

            
            adress_short =  f"{street}, {city}"
            return (formatted_address,adress_short,street,city)
        
        return (street, street, street, None)

    async def get_pois(self):
        url = self.get_url()
        http_timeout = 15
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
            raise RadarWarningConnectionError("HTTP error occurred",
                response.status, json.loads(contents.decode("utf8"))
            )

        data_pois = await response.json()
        pois = list()

        if 'pois' in data_pois and len(data_pois['pois']) > 0:
            for poi in data_pois['pois']:
                poi['info'] = json.loads(poi['info'])

            # Datenstruktur ausgeben
            for poi_data in data_pois['pois']:
                start_point = Point(self.latitude, self.longitude)
                end_point = Point(poi_data['lat'], poi_data['lng'])
                distance = geodesic(start_point, end_point).kilometers
                if distance <= self.radius_km:
                    poi_street = poi_data.get('street', None)
                    adress, adress_short, street, city = await self.get_adress(end_point, poi_street)
                    poi = POI(
                        id=poi_data['id'],
                        latitude=poi_data['lat'],
                        longitude=poi_data['lng'],
                        street=street,
                        vmax=poi_data.get('vmax',0),
                        distance=distance,
                        adress=adress,
                        adress_short = adress_short,
                        city = city
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
