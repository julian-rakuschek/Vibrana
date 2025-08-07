import json
import os
import shutil
from pathlib import Path

import numpy as np

from parser.lib.dewesoft.dwparser import process_file

meta = {
    "name": "Vibration Signal provided by Dewesoft",
    "description": "",
    "task": "Changepoint Detection",
    "source": "Konrad Schweiger",
}

def parse_dewe():
    raw_file_path = os.path.join(Path(__file__).parents[2], "data", "raw-signals", "dewesoft-konrad-schweiger", "bearing.dxd")
    dataset_folder = os.path.join(Path(__file__).parents[2], "data", "prepared-signals", "streams", "dewesoft-konrad-schweiger")
    subset_folder = os.path.join(dataset_folder, "bearing")

    if not os.path.exists(raw_file_path):
        print(f"Could not find {raw_file_path}")
        return
    shutil.rmtree(dataset_folder, ignore_errors=True)
    Path(subset_folder).mkdir(parents=True, exist_ok=True)

    values, timestamps, _ = process_file(raw_file_path)
    np.save(os.path.join(subset_folder, "values.npy"), values)
    np.save(os.path.join(subset_folder, "timestamps.npy"), timestamps)

    with open(os.path.join(dataset_folder, "meta.json"), "w") as f:
        f.write(json.dumps(meta, indent=4))


if __name__ == '__main__':
    parse_dewe()
