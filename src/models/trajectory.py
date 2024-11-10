import numpy as np

from src.models.refpoint import RefPoint
from src.models.mapedge import MapEdge
from src.models.maptree import MapTree


class Trajectory:
    def __init__(self,
                 lat: np.ndarray,
                 lon: np.ndarray,
                 time: np.ndarray,
                 ids: np.ndarray):
        """

        Parameters
        ----------
        lat - The latitude array of the trajectory
        lon - The longitude array of the trajectory
        time - The time array of the trajectory in milliseconds
        """
        assert len(lat) == len(lon) == len(time) == len(ids)

        self.lat = lat
        self.lon = lon
        self.time = time
        self.dt = np.diff(time)
        self.ids = ids

    def __len__(self) -> int:
        return len(self.lat)

    def merge(self, map_lat: np.ndarray,
                    map_lon: np.ndarray) -> MapTree:
        lat, lon, ids = self.lat, self.lon, self.ids
        map_tree: MapTree = MapTree()
        j = 0
        for i in range(map_lat.shape[0] - 1):
            pt0 = RefPoint(float(map_lat[i]), float(map_lon[i]))
            pt1 = RefPoint(float(map_lat[i + 1]), float(map_lon[i + 1]))
            seg_len = pt0.haversine(*pt1.to_tuple())

            map_edge = MapEdge()
            map_edge.append(pt0)
            while j < lat.shape[0]:
                match_pt = RefPoint(float(lat[j]), float(lon[j]), int(ids[j]))
                len_ini = pt0.haversine(*match_pt.to_tuple())
                len_end = pt1.haversine(*match_pt.to_tuple())

                if len_ini <= seg_len and len_end <= seg_len:
                    map_edge.append(match_pt)
                    j += 1
                else:
                    map_edge.append(pt1)
                    map_tree.append(map_edge)
                    break
            else:
                map_edge.append(pt1)
                map_tree.append(map_edge)
        return map_tree
