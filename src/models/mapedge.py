from src.models.pointlist import PointList


class MapEdge(PointList):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"MapEdge({self.points})"
