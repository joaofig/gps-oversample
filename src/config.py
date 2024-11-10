import tomli

from typing import Dict
from pathlib import Path


def load_config() -> Dict:
    return tomli.loads(Path("./config.toml").read_text(encoding="utf-8"))
