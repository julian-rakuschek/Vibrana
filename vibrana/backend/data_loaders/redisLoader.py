import datetime
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import redis
from fastparquet.writer import overwrite
from redis import Redis
from tqdm import tqdm

from vibrana.backend.data_loaders.dataLoaderBase import DataLoaderBase
from vibrana.backend.helper.config import get_config

conf = get_config()

def get_redis() -> Redis:
    host = conf["redis"]["host"]
    if os.environ.get('DOCKER', "False") == 'True':
        host = conf["redis"]["docker_host"]
    port = conf["redis"]["port"]
    return redis.Redis(host=host, port=port, db=1)

def clear_all_redis():
    r = get_redis()
    for key in r.scan_iter("vibrana:*"):
        r.delete(key)


def estimate_sampling_frequency(meta: dict) -> float:
    start = datetime.datetime.fromisoformat(meta["start_time"])
    end = datetime.datetime.fromisoformat(meta["end_time"])
    total_samples = meta["total_sample_points"]
    duration_seconds = (end - start).total_seconds()
    return total_samples / duration_seconds


class RedisLoader(DataLoaderBase):
    def __init__(self, path_to_npy, dataset, subset):
        super().__init__()
        self.path_to_npy = path_to_npy
        self.redis_prefix = f"vibrana:{dataset}:{subset}"
        self.dataset = dataset
        self.subset = subset
        self.r = get_redis()

        time_file = os.path.join(Path(path_to_npy).parents[0], "time.json")
        with open(time_file, "r") as f:
            self.fs = estimate_sampling_frequency(json.load(f))

    def load_numpy_file(self, overwrite_existing=False):
        lock_key = f"{self.redis_prefix}:lock"
        lock = self.r.lock(lock_key, timeout=None, blocking_timeout=None)
        lock.acquire()
        data_key = f"{self.redis_prefix}:data"
        if not overwrite_existing and self.r.exists(data_key):
            self.data_size = self.r.llen(data_key)
            lock.release()
            return
        self.r.delete(data_key)
        data = np.load(self.path_to_npy)
        print(f"Loading {data_key} into redis with size {len(data)}")
        pipe = self.r.pipeline()
        batch_size = 1000
        data_size = 0
        for i in tqdm(range(0, len(data), batch_size)):
            batch = data[i:i + batch_size].tolist()
            pipe.rpush(data_key, *batch)
            data_size += len(batch)
        pipe.execute()
        self.data_size = data_size
        print("Done!")
        lock.release()

    def get_slice(self, start_index=0, end_index=-1, as_numpy=True):
        self.load_numpy_file()
        data_key = f"{self.redis_prefix}:data"
        retrieved = self.r.lrange(data_key, start_index, end_index)
        retrieved = [float(x) for x in retrieved]
        if as_numpy:
            retrieved = np.array(retrieved)
        return retrieved

    def clear(self, only_vectors=True):
        pattern = f"{self.redis_prefix}:*"
        if only_vectors:
            pattern = f"{self.redis_prefix}:vectors:*"
        for key in self.r.scan_iter(pattern):
            self.r.delete(key)


if __name__ == '__main__':
    clear_all_redis()
    exit(0)
    dataset = "hydro"
    subset = "x"
    file_path_data = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "values.npy")
    file_path_ts = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "timestamps.npy")
    loader = RedisLoader(file_path_data, dataset, subset)
    loader.load_numpy_file(overwrite_existing=False)
    slice = loader.get_slice(timestamps=True)
    print(slice)
    print(len(slice))
    # ts = loader.get_timestamp_subsample()
    # print(ts)
    loader.clear(only_vectors=False)