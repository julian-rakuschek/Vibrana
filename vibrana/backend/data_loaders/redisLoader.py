import math
import os
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

class RedisLoader(DataLoaderBase):
    def __init__(self, path_to_npy, dataset, subset):
        super().__init__()
        self.path_to_npy = path_to_npy
        self.path_to_timestamps = os.path.join(Path(path_to_npy).parents[0], "timestamps.npy")
        self.redis_prefix = f"vibrana:{dataset}:{subset}"
        self.dataset = dataset
        self.subset = subset
        self.r = get_redis()

    def load_numpy_file(self, overwrite_existing=False):
        data_key = f"{self.redis_prefix}:data"
        timestamps_key = f"{self.redis_prefix}:timestamps"
        if not overwrite_existing and self.r.exists(data_key):
            self.data_size = self.r.llen(data_key)
            return
        self.r.delete(data_key)
        self.r.delete(timestamps_key)
        data = np.load(self.path_to_npy)
        timestamps = np.arange(len(data))
        if os.path.exists(self.path_to_timestamps):
            timestamps = np.load(self.path_to_timestamps)
            if len(timestamps) != len(data):
                print("WARNING: timestamps and data values differ in length! Using default timestamps as fallback")
        print(f"Loading {data_key} into redis with size {len(data)}")
        pipe = self.r.pipeline()
        batch_size = 1000
        data_size = 0
        for i in tqdm(range(0, len(data), batch_size)):
            batch = data[i:i + batch_size].tolist()
            batch_ts = timestamps[i:i + batch_size].tolist()
            pipe.rpush(data_key, *batch)
            pipe.rpush(timestamps_key, *batch_ts)
            data_size += len(batch)
        pipe.execute()
        self.data_size = data_size
        print("Done!")

    def get_slice(self, start_index=0, end_index=-1, as_numpy=True, timestamps=False):
        self.load_numpy_file()
        data_key = f"{self.redis_prefix}:timestamps" if timestamps else f"{self.redis_prefix}:data"
        retrieved = self.r.lrange(data_key, start_index, end_index)
        retrieved = [float(x) for x in retrieved]
        if as_numpy:
            retrieved = np.array(retrieved)
        return retrieved

    def get_timestamp_subsample(self, start_index=0, end_index=-1, as_numpy=True, amount=1000):
        self.load_numpy_file()
        data_key = f"{self.redis_prefix}:timestamps"

        if end_index == -1:
            end_index = self.data_size - 1
        if start_index < 0:
            start_index = self.data_size + start_index
        if end_index < 0:
            end_index = self.data_size + end_index

        step = self.data_size // amount
        indices = range(start_index, end_index + 1, step)

        pipe = self.r.pipeline()
        for i in indices:
            pipe.lindex(data_key, i)

        retrieved = [float(x) for x in pipe.execute()]
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
    dataset = "nasa-run-to-failure"
    subset = "test2"
    file_path_data = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "values.npy")
    file_path_ts = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "timestamps.npy")
    loader = RedisLoader(file_path_data, dataset, subset, path_to_timestamps=file_path_ts)
    loader.load_numpy_file(overwrite_existing=True)
    slice = loader.get_slice(timestamps=True)
    print(slice)
    ts = loader.get_timestamp_subsample()
    print(ts)
    loader.clear(only_vectors=False)