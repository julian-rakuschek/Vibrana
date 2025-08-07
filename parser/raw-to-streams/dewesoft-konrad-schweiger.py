import os
import shutil
from pathlib import Path

import numpy as np

from parser.lib.dewesoft.dwparser import process_file


def parse_dewe():
    raw_file_path = os.path.join(Path(__file__).parents[2], "data", "raw-signals", "dewesoft-konrad-schweiger", "bearing.dxd")
    file_parsed_folder = os.path.join(Path(__file__).parents[2], "data", "prepared-signals", "streams", "dewesoft-konrad-schweiger", "bearing")

    if not os.path.exists(raw_file_path):
        print(f"Could not find {raw_file_path}")
        return
    shutil.rmtree(file_parsed_folder, ignore_errors=True)
    Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)

    values, timestamps, _ = process_file(raw_file_path)
    np.save(os.path.join(file_parsed_folder, "values.npy"), values)
    np.save(os.path.join(file_parsed_folder, "timestamps.npy"), timestamps)


if __name__ == '__main__':
    parse_dewe()
