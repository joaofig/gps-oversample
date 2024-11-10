from typing import List
from src.models.refpoint import RefPoint


class PointList:
    def __init__(self):
        self.points: List[RefPoint] = []
        self.distances: List[float] = []
        self.bearings: List[float] = []

    def __repr__(self):
        return f"PointList({self.points})"

    def __len__(self):
        return len(self.points)

    def append(self, point: RefPoint) -> None:
        self.points.append(point)
        if len(self.points) > 1:
            self.distances.append(self.points[-2].distance_to(point))
            self.bearings.append(self.points[-2].bearing_to(point))
