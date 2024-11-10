import numpy as np
import pandas as pd

from typing import List
from src.dbtool import get_eved_db, get_traj_db
from src.geo.geomath import decode_polyline, delta_location, vec_haversine, num_haversine
from src.models.deadreckon import DeadReckon
from src.models.gpssegment import GpsSegment
from src.models.trajectory import Trajectory
from tqdm import tqdm


def load_trajectories() -> pd.DataFrame:
    db = get_eved_db()
    traj_df = db.load_trajectories()
    return traj_df


def load_trajectory_signals(traj_id: int) -> pd.DataFrame:
    db = get_eved_db()
    return db.load_trajectory_signals(traj_id)


def load_polyline(traj_id: int) -> str:
    db = get_traj_db()
    return db.get_polyline(traj_id)


def insert_dead_reckon(locations: List[DeadReckon]) -> None:
    db = get_eved_db()

    lat = np.array([p.latitude for p in locations])
    lon = np.array([p.longitude for p in locations])
    t = [p.t for p in locations]
    signal_ids = [p.signal_id for p in locations]

    x = np.append([0.0], vec_haversine(lat[:-1], lon[:-1], lat[1:], lon[1:])).cumsum()

    speed = np.gradient(x, t)
    accel = np.gradient(speed, t)
    jerk = np.gradient(accel, t)
    db.save_dead_reckoning(signal_ids, t, lat, lon, x, speed, accel, jerk)


def integrate_speeds(seg_df: pd.DataFrame) -> np.ndarray:
    time_stamp = seg_df["time_stamp"].to_numpy() / 1000.0
    speed = seg_df["speed"].to_numpy() / 3.6

    dt = np.diff(time_stamp)
    mv = (speed + np.roll(speed, -1))[:-1] / 2.0
    dx = dt * mv
    return dx


def dead_reckon(gps_segment: GpsSegment,
                distances: np.ndarray,
                gps_ids: np.ndarray,
                timestamps: np.ndarray) -> List[DeadReckon]:
    locations: List[DeadReckon] = [
        DeadReckon(signal_id = int(gps_ids[0]),
                   latitude=gps_segment.points[0].lat,
                   longitude=gps_segment.points[0].lon,
                   t=float(timestamps[0]))
    ]
    d = 0.0
    i_gps = 1
    i_dx = 0

    for distance, signal_id in zip(distances, gps_ids[1:]):
        d += distance

        if d >= gps_segment.distances[i_dx]:
            d -= gps_segment.distances[i_dx]
            i_dx += 1

            if i_dx >= len(gps_segment.distances):
                while i_gps < len(gps_ids) - 1:
                    locations.append(DeadReckon(signal_id = int(gps_ids[i_gps]),
                                                latitude=gps_segment.points[i_dx-1].lat,
                                                longitude=gps_segment.points[i_dx-1].lon,
                                                t=float(timestamps[i_gps])))
                    i_gps += 1
                break

        if i_gps < len(gps_ids) - 1:
            lat, lon = delta_location(*gps_segment.points[i_dx].to_tuple(),
                                      gps_segment.bearings[i_dx], d)
            locations.append(
                DeadReckon(signal_id = int(signal_id), latitude = lat, longitude = lon,
                           t = float(timestamps[i_gps]))
            )
            i_gps += 1

    return locations


def compute_gps_segments(unique_df: pd.DataFrame,
                         polyline: np.ndarray) -> List[GpsSegment]:
    traj = Trajectory(lat=unique_df["match_latitude"].to_numpy(),
                      lon=unique_df["match_longitude"].to_numpy(),
                      time=unique_df["time_stamp"].to_numpy() / 1000.0,
                      ids=unique_df["signal_id"].to_numpy())

    map_tree = traj.merge(map_lat=polyline[:, 0],  # Latitude
                          map_lon=polyline[:, 1])  # Longitude

    gps_segments = map_tree.get_segments()
    return gps_segments


def update_schema():
    db = get_eved_db()
    db.update_schema()


def main():
    traj_df = load_trajectories()
    traj_ids = traj_df["traj_id"].to_numpy()

    # traj_ids = [233]

    update_schema()

    for traj_id in tqdm(traj_ids):
        polyline_str = load_polyline(int(traj_id))

        if polyline_str is not None and len(polyline_str):
            signals_df = load_trajectory_signals(int(traj_id))
            unique_df = signals_df.drop_duplicates(subset=["match_latitude", "match_longitude"], keep="first")
            polyline = np.array(decode_polyline(polyline_str, order="latlon"))

            gps_segments = compute_gps_segments(unique_df, polyline)

            locations: List[DeadReckon] = []
            for gps_segment in gps_segments:
                segment_dx = sum(gps_segment.distances)

                # Extract the kinematics data for this segment
                seg_df = signals_df[(signals_df["signal_id"] >= gps_segment.points[0].seq) &
                                    (signals_df["signal_id"] <= gps_segment.points[-1].seq)]
                if seg_df.shape[0] > 1:
                    # Infer the point in-between using kinematics
                    dxs = integrate_speeds(seg_df)
                    dx = np.sum(dxs)

                    if dx > 0.0:
                        r = segment_dx / dx
                        corrected_dxs = r * dxs
                        signal_ids = seg_df["signal_id"].to_numpy()
                        timestamps = seg_df["time_stamp"].to_numpy() / 1000.0
                        dr = dead_reckon(gps_segment,
                                         corrected_dxs,
                                         signal_ids,
                                         timestamps)
                        locations.extend(dr)

            if len(locations) > 1:
                insert_dead_reckon(locations)


if __name__ == '__main__':
    main()
