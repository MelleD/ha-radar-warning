import json
import requests
from geopy.distance import geodesic
from geopy.point import Point
from datetime import UTC, datetime

from .const import (
    LOGGER
)

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
        self.pois = set()

    def __len__(self):
        """Return the count of pois."""
        return len(self.pois)

    def get_coordinates(self, direction: float):
        start_point = Point(self.latitude, self.longitude)
        distance = geodesic(kilometers=self.radius_km).destination(start_point, direction)  
        return distance.latitude, distance.longitude

    def get_url(self, direction: float):
        get_type = "0,1,2,3,4,5,6"
        coordinates  = self.get_coordinates(direction)
        coordinates_latitude=coordinates[0]
        coordinates_longitude=coordinates[1]
        return f"https://cdn2.atudo.net/api/1.0/vl.php?type={get_type}&box={self.latitude},{self.longitude},{coordinates_latitude},{coordinates_longitude},{coordinates_latitude},{coordinates_longitude},{self.latitude},{self.longitude}"


    def get_poi(self, direction: float):
        url = self.get_url(direction)
        pois = set()
        http_timeout = 5
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


    def update_pois(self):
        self.last_update = None
        all_pois = set()

        directions = [1, 181, 91, 270, 45, 225, 135, 320]

        for direction in directions:
            pois = self.get_poi(direction)
            all_pois.update(pois)

        # Ausgabe der gesammelten POIs
        for poi in all_pois:
            LOGGER.debug(poi)

        self.last_update = datetime.now(UTC)
        self.pois = all_pois
