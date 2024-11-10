from dataclasses import dataclass


@dataclass
class DeadReckon:
    signal_id: int
    t: float
    latitude: float
    longitude: float
