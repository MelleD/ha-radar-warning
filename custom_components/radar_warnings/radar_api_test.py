import asyncio
import json
import socket
import aiohttp
import math
from geopy.distance import geodesic
from geopy.point import Point
from datetime import UTC, datetime

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

    def __repr__(self):
        return (f"POI(ID={self.id}, Straße={self.street}, "
                f"Koordinaten=({self.latitude},{self.longitude}), "
                f"Max Geschwindigkeit={self.vmax} km/h, Distanz={self.distance:.2f} km)")

class RadarWarningApi:
    def __init__(self,latitude: float, longitude: float, radius_km: float):
        self.latitude = latitude
        self.longitude = longitude 
        self.radius_km = radius_km
        self.last_update = None
        self.pois = self.update_pois()

    def __len__(self):
        """Return the count of pois."""
        return len(self.pois)

    def get_url(self):
        get_type = "0,1,2,3,4,5,6"
        area_top_right_coordinates = self.blitzer_get_coordinates(45)
        area_top_right_latitude=area_top_right_coordinates[0]
        area_top_right_longitude=area_top_right_coordinates[1]
        area_top_left_coordinates = self.blitzer_get_coordinates(225)
        area_top_left_latitude=area_top_left_coordinates[0]
        area_top_left_longitude=area_top_left_coordinates[1]

        return f"https://cdn2.atudo.net/api/1.0/vl.php?type={get_type}&box={area_top_left_latitude},{area_top_left_longitude},{area_top_right_latitude},{area_top_right_longitude}"


    def get_poi(self):
        url = self.get_url()
        pois = set()
        http_timeout = 5

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    auth=auth,
                    data=data,
                    json=json_data,
                    params=params,
                    headers=headers,
                    ssl=self.verify_ssl,
                    skip_auto_headers=skip_auto_headers,
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to AdGuard Home instance."
            raise AdGuardHomeConnectionError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with AdGuard Home."
            raise AdGuardHomeConnectionError(msg) from exception






        response = requests.get(url, timeout=http_timeout)
        response.raise_for_status()
        data = response.json()

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
                    street=poi_data['street'],
                    vmax=poi_data['vmax'],
                    distance=distance
                )
                pois.add(poi)

        return pois
    
    def blitzer_get_coordinates(self, grad: int):
        abstand = math.sqrt(self.radius_km*self.radius_km + self.radius_km*self.radius_km) * 1000  # Angabe in Meter!
        
        # Wegpunktprojektion berechnen
        dnord = (math.cos(math.radians(grad)) * abstand) / 1850  # Ergebnis in Grad
        dost = (math.sin(math.radians(grad)) * abstand) / (1850 * math.cos(math.radians(self.latitude)))
        new_lat = self.latitude + dnord / 60
        new_lng = self.longitude + dost / 60
        
        return new_lat, new_lng


    def update_pois(self):
        print("Start update_pois")
        self.last_update = None
        all_pois = self.get_poi()

        # Ausgabe der gesammelten POIs
        for poi in all_pois:
            print(poi)

        self.last_update = datetime.now(UTC)
        self.pois = all_pois

api = RadarWarningApi(48.644854635295175,8.895243108272554,20)
#api = RadarWarningApi(52.288659,13.411855,20)