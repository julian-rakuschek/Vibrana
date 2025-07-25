import json
from pathlib import Path


def get_config():
    with open(f"{str(Path(__file__).parents[1])}/config.json", "r", encoding="utf-8") as f:
        return json.load(f)

