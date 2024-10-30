import os
from pathlib import Path

import numpy as np

folder_path = os.path.join(Path(__file__).parents[1], "data", "raw", "nasa-bearings", "test2")
parsed_folder = os.path.join(Path(__file__).parents[1], "data", "parsed", "nasa-bearings", "test2")
Path(parsed_folder).mkdir(parents=True, exist_ok=True)

for file in os.listdir(folder_path):
    data = np.loadtxt(os.path.join(folder_path, file))
    channel_data = data[:, 0]
    np.save(os.path.join(parsed_folder, f"values-{file}.npy"), channel_data)

