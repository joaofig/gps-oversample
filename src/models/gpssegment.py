from src.models.refpoint import RefPoint
from src.models.pointlist import PointList
from src.models.mapedge import MapEdge


class GpsSegment(PointList):
    def __init__(self,
                 point: RefPoint):
        super().__init__()
        self.append(point)

    def __repr__(self):
        return f"GpsSegment({self.points})"

    def append_edge(self, edge: MapEdge) -> None:
        for point in edge.points:
            self.append(point)
