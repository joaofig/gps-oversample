import os

from src.db.api import BaseDb


class TrajDb(BaseDb):

    def __init__(self, folder="./db"):
        super().__init__(folder=folder, file_name="eved_traj.db")

        if not os.path.exists(self.db_file_name):
            self.create_schema(schema_dir='schema/eved_traj')

    def get_node_location(self, node: int) -> tuple[float, float] | None:
        sql = "select lat, lon from h3_node where h3=?"
        res = self.query(sql, [node])
        if res is not None and len(res) > 0:
            return res[0]
        else:
            return None

    def get_polyline(self, traj_id: int) -> str:
        sql = "select geometry from traj_match where traj_id=?"
        return self.query_scalar(sql, [traj_id])
