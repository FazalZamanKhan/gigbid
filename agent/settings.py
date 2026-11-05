"""Development configuration loader; policy data stays outside graph code."""

from functools import lru_cache
from pathlib import Path
import yaml


@lru_cache(maxsize=1)
def load_config() -> dict:
    path = Path(__file__).with_name("config.yaml")
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)
