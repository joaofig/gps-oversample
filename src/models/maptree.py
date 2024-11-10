from typing import List
from src.models.mapedge import MapEdge
from src.models.gpssegment import GpsSegment


class MapTree:
    def __init__(self):
        self.edges: List[MapEdge] = []

    def append(self, edge: MapEdge) -> None:
        self.edges.append(edge)

    def get_segments(self) -> List[GpsSegment]:
        segments: List[GpsSegment] = []
        segment: GpsSegment | None = None

        for edge in self.edges:
            for point in edge.points:
                if point.seq == -1:
                    # This is a map vertex
                    if segment is not None and point != segment.points[-1]:
                        segment.append(point)
                else:
                    # This is a GPS sample
                    if segment is None:
                        segment = GpsSegment(point=point)
                    else:
                        segment.append(point=point)
                        segments.append(segment)
                        segment = GpsSegment(point=point)
        return segments
