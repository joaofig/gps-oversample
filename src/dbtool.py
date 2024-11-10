from src.config import load_config
from src.db.eved import EVedDb
from src.db.trajdb import TrajDb


def get_eved_db() -> EVedDb:
    config = load_config()
    return EVedDb(folder=config["database"]["folder"])


def get_traj_db() -> TrajDb:
    config = load_config()
    return TrajDb(folder=config["database"]["folder"])
