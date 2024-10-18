import os
from pathlib import Path

samples_folder = os.path.join(Path(__file__).parents[2], "data", "split")
data_folder = os.path.join(Path(__file__).parents[2], "data")

READ_ONLY = bool(os.environ.get("READ_ONLY", "False") == "True")
