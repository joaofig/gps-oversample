from src.geo.geomath import num_haversine, num_bearing
from dataclasses import dataclass
from typing import Tuple


@dataclass
class LatLon:
    lat: float
    lon: float

    def haversine(self, lat: float, lon: float) -> float:
        return num_haversine(self.lat, self.lon, lat, lon)

    def distance_to(self, lat_lon: 'LatLon') -> float:
        return self.haversine(lat_lon.lat, lat_lon.lon)

    def bearing_to(self, lat_lon: 'LatLon') -> float:
        return num_bearing(self.lat, self.lon, lat_lon.lat, lat_lon.lon)

    def to_tuple(self) -> Tuple[float, float]:
        return self.lat, self.lon
