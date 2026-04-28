import datetime
import json
import os
from pathlib import Path

import numpy as np

from vibrana.backend.data_loaders.dataLoaderBase import DataLoaderBase
from vibrana.backend.helper.config import get_config

conf = get_config()

def estimate_sampling_frequency(meta: dict) -> float:
    start = datetime.datetime.fromisoformat(meta["start_time"])
    end = datetime.datetime.fromisoformat(meta["end_time"])
    total_samples = meta["total_sample_points"]
    duration_seconds = (end - start).total_seconds()
    return total_samples / duration_seconds


class DiskLoader(DataLoaderBase):
    def __init__(self, path_to_npy, dataset, subset):
        super().__init__()
        self.path_to_npy = path_to_npy
        self.dataset = dataset
        self.subset = subset
        time_file = os.path.join(Path(path_to_npy).parents[0], "time.json")
        with open(time_file, "r") as f:
            self.fs = estimate_sampling_frequency(json.load(f))
        self.array = np.load(path_to_npy, mmap_mode="r")

    def get_slice(self, start_index=0, end_index=-1):
        return self.array[start_index:end_index]



if __name__ == '__main__':
    dataset = "hydro"
    subset = "x"
    path = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "values.npy")
    loader = DiskLoader(path, dataset, subset)
    print(loader.get_slice(1000, 2000))
