import json
import os
import shutil
from pathlib import Path

import numpy as np
from tqdm import tqdm

meta = {
    "name": "UCR Engine Fault Detection",
    "description": "Vibrations acquired from an engine, showing multiple runs (with and without damage). The subsets highlight the difference if noise is applied.",
    "task": "Classification",
    "source": "https://www.timeseriesclassification.com/description.php?Dataset=FaultDetectionA",
}

def process_engine_failures(max_ts=100):
    raw_file_path = os.path.join(Path(__file__).parents[2], "data", "raw-signals", "ucr-engine-fault-detection", "FaultDetectionA_TRAIN.ts")
    dataset_folder = os.path.join(Path(__file__).parents[2], "data", "prepared-signals", "chunks", "fault-detection")
    file_parsed_folder = os.path.join(dataset_folder, "fault-detection-A")

    if not os.path.exists(raw_file_path):
        print(f"Could not find {raw_file_path}")
        return
    shutil.rmtree(file_parsed_folder, ignore_errors=True)
    Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)

    with open(os.path.join(dataset_folder, "meta.json"), "w") as f:
        f.write(json.dumps(meta, indent=4))

    undamaged_count, inner_count, outer_count = 0, 0, 0

    with open(raw_file_path, "r") as f:
        for line in f.readlines():
            if line.startswith("@"):
                continue
            data, class_ = line.split(":")
            class_ = class_.strip().replace("\n", "")
            print(class_)
            data = np.array(data)
            if class_ == "0" and undamaged_count < max_ts:
                np.save(os.path.join(file_parsed_folder, f"values-undamaged-{str(undamaged_count).zfill(4)}.npy"), data)
                undamaged_count += 1
            if class_ == "1" and inner_count < max_ts:
                np.save(os.path.join(file_parsed_folder, f"values-inner-{str(inner_count).zfill(4)}.npy"), data)
                inner_count += 1
            if class_ == "2" and outer_count < max_ts:
                np.save(os.path.join(file_parsed_folder, f"values-outer-{str(outer_count).zfill(4)}.npy"), data)
                outer_count += 1
            if undamaged_count == max_ts and inner_count == max_ts and outer_count == max_ts:
                break




if __name__ == '__main__':
    process_engine_failures(20)
