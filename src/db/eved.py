import os
from typing import List

import numpy as np
import pandas as pd

from src.db.api import BaseDb
from src.models.deadreckon import DeadReckon
from src.models.refpoint import RefPoint


class EVedDb(BaseDb):

    def __init__(self, folder='./db'):
        super().__init__(folder=folder, file_name='eved.db')

        if not os.path.exists(self.db_file_name):
            self.create_schema(schema_dir='schema/eved')

    def insert_signals(self, signals):
        self.insert_list("signal/insert", signals)

    def load_trajectories(self) -> pd.DataFrame:
        sql = "select traj_id, vehicle_id, trip_id from trajectory"
        return self.query_df(sql)

    def load_trajectory_signals(self, traj_id: int) -> pd.DataFrame:
        sql = """
        select      s.signal_id
        ,           s.match_latitude
        ,           s.match_longitude
        ,           dr.t
        ,           dr.latitude
        ,           dr.longitude
        ,           dr.speed
        ,           dr.accel
        ,           dr.jerk
        from        signal s 
        inner join  trajectory t on s.trip_id = t.trip_id and s.vehicle_id = t.vehicle_id
        left join   dead_reckon dr on dr.signal_id = s.signal_id
        where       t.traj_id = ?
        order by    s.time_stamp
        """
        return self.query_df(sql, [traj_id])


    def load_dr_trajectory(self, traj_id: int) -> pd.DataFrame:
        sql = """
        select      s.signal_id
        ,           s.match_latitude
        ,           s.match_longitude
        ,           dr.latitude
        ,           dr.longitude
        ,           dr.jerk
        from        signal s 
        inner join  trajectory t on s.trip_id = t.trip_id and s.vehicle_id = t.vehicle_id
        left join   dead_reckon dr on dr.signal_id = s.signal_id
        where       t.traj_id = ?
        order by    s.time_stamp        
        """
        return self.query_df(sql, [traj_id])


    def update_schema(self) -> None:
        if not self.table_exists("dead_reckon"):
            sql = """
            create table dead_reckon (
                signal_id   integer primary key,
                t           double not null,
                latitude    double not null,
                longitude   double not null,
                x           double not null,
                speed       double not null,
                accel       double not null,
                jerk        double not null,
                is_node     integer not null default 0
            )
            """
            self.execute_sql(sql)


    def save_dead_reckoning(self,
                            signal_ids: List[int],
                            timestamps: List[float],
                            latitudes: np.ndarray,
                            longitudes: np.ndarray,
                            xs: np.ndarray,
                            speed: np.ndarray,
                            accel: np.ndarray,
                            jerk: np.ndarray) -> None:
        sql = """
        insert into dead_reckon 
            (signal_id, t, latitude, longitude, x, speed, accel, jerk)
        values
            (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params =  [(signal_id, t, lat, lon, x, s, a, j)
                   for signal_id, t, lat, lon, x, s, a, j in
                   zip(signal_ids, timestamps, latitudes, longitudes, xs, speed, accel, jerk)]
        self.execute_sql(sql, params, many=True)
