import json
import os
import shutil
from pathlib import Path

import numpy as np
from tqdm import tqdm

meta = {
    "name": "Engine Run To Failure",
    "description": "Vibrations acquired from the bearing of an engine in a run-to-failure setting.",
    "task": "Changepoint Detection",
    "source": "https://www.kaggle.com/datasets/vinayak123tyagi/bearing-dataset",
}

def process_run_to_failure(subset, channel):
    raw_files_folder = os.path.join(Path(__file__).parents[1], "data", "raw-signals", "nasa-run-to-failure", subset)
    dataset_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "nasa-run-to-failure")
    subset_folder = os.path.join(dataset_folder, subset)

    if not os.path.exists(raw_files_folder):
        print(f"Could not find {raw_files_folder}")
        return
    shutil.rmtree(dataset_folder, ignore_errors=True)
    Path(subset_folder).mkdir(parents=True, exist_ok=True)

    total_signal = np.array([])
    for file in tqdm(os.listdir(raw_files_folder)):
        file_path = os.path.join(raw_files_folder, file)
        data = np.loadtxt(file_path)
        total_signal = np.concatenate([total_signal, data[:, channel]])
    print(total_signal.shape)
    np.save(os.path.join(subset_folder, "values.npy"), total_signal)

    with open(os.path.join(dataset_folder, "meta.json"), "w") as f:
        f.write(json.dumps(meta, indent=4))


if __name__ == '__main__':
    process_run_to_failure("test2", 0)
