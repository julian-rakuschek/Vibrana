import os
from pathlib import Path

import numpy as np


def parse_file(file_path):
    motors = {
        "undamaged": [],
        "inner": [],
        "outer": []
    }
    with open(file_path, "r") as f:
        for line in f.readlines():
            if line.startswith("@"):
                continue
            arr, cls = line.split(":")
            arr = np.fromstring(arr, sep=",")
            cls = int(cls)
            if cls == 0:
                motors["undamaged"].append(arr)
            elif cls == 1:
                motors["inner"].append(arr)
            else:
                motors["outer"].append(arr)
    return motors


def save_parsed_subset():
    file_path = os.path.join(Path(__file__).parents[1], "data", "raw", "motor", "FaultDetectionB_TRAIN.ts")
    file_parsed_folder = os.path.join(Path(__file__).parents[1], "data", "parsed", "motor", "inner-damage")
    file_parsed_folder_noise = os.path.join(Path(__file__).parents[1], "data", "parsed", "motor", "inner-damage-noise")
    Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)
    Path(file_parsed_folder_noise).mkdir(parents=True, exist_ok=True)

    motors = parse_file(file_path)
    inner_subset = [2, 4, 12, 16, 18]
    undamaged_subset = [7, 8, 9, 10, 11]

    for index in inner_subset:
        inner = motors["inner"][index]
        inner_noise = inner + np.random.normal(0, 2, len(inner))
        np.save(os.path.join(file_parsed_folder, f"values-inner-{str(index).zfill(2)}.npy"), inner)
        np.save(os.path.join(file_parsed_folder_noise, f"values-inner-noise-{str(index).zfill(2)}.npy"), inner_noise)

    for index in undamaged_subset:
        undamaged = motors["undamaged"][index]
        undamaged_noise = undamaged + np.random.normal(0, 2, len(undamaged))
        np.save(os.path.join(file_parsed_folder, f"values-undagamed-{str(index).zfill(2)}.npy"), undamaged)
        np.save(os.path.join(file_parsed_folder_noise, f"values-undagamed-noise-{str(index).zfill(2)}.npy"), undamaged_noise)


if __name__ == '__main__':
    save_parsed_subset()
