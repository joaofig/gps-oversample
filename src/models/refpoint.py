from src.models.latlon import LatLon
from dataclasses import dataclass


@dataclass
class RefPoint(LatLon):
    seq: int = -1
