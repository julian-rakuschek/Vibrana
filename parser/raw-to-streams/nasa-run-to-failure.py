import os
import shutil
from pathlib import Path

import numpy as np
from tqdm import tqdm


def process_run_to_failure(subset, channel):
    raw_files_folder = os.path.join(Path(__file__).parents[2], "data", "raw-signals", "nasa-run-to-failure", subset)
    file_parsed_folder = os.path.join(Path(__file__).parents[2], "data", "prepared-signals", "streams", "nasa-run-to-failure", subset)

    if not os.path.exists(raw_files_folder):
        print(f"Could not find {raw_files_folder}")
        return
    shutil.rmtree(file_parsed_folder, ignore_errors=True)
    Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)

    total_signal = np.array([])
    for file in tqdm(os.listdir(raw_files_folder)):
        file_path = os.path.join(raw_files_folder, file)
        data = np.loadtxt(file_path)
        total_signal = np.concatenate([total_signal, data[:, channel]])
    print(total_signal.shape)
    np.save(os.path.join(file_parsed_folder, "values.npy"), total_signal)


if __name__ == '__main__':
    process_run_to_failure("test2", 0)
