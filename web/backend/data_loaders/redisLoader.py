import os
import pickle
from pathlib import Path

import numpy as np
import redis
from tqdm import tqdm

from web.backend.data_loaders.dataLoaderBase import DataLoaderBase


class RedisLoader(DataLoaderBase):
    def __init__(self, path_to_npy, redis_prefix):
        super().__init__()
        self.path_to_npy = path_to_npy
        self.redis_prefix = redis_prefix
        redis_host = "localhost"
        if os.environ.get('DOCKER', "False") == 'True':
            redis_host = "anoscout_redis"
        self.r = redis.Redis(host=redis_host, port=6379, db=1)

    def load_numpy_file(self, overwrite_existing=False):
        data_key = f"{self.redis_prefix}:data"
        if not overwrite_existing and self.r.exists(data_key):
            self.data_size = self.r.llen(data_key)
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

    def get_slice(self, start=0, end=-1):
        self.load_numpy_file()
        data_key = f"{self.redis_prefix}:data"
        retrieved = self.r.lrange(data_key, start, end)
        retrieved = np.array([float(x) for x in retrieved])
        return retrieved

    def store_hyperplane_vectors(self, v1: np.ndarray, v2: np.ndarray, start: int, window_size: int):
        data_key = f"{self.redis_prefix}:vectors:{start}:{window_size}"
        data = {"v1": v1, "v2": v2, "start": start, "window_size": window_size}
        serialized = pickle.dumps(data)
        self.r.set(data_key, serialized)

    def retrieve_hyperplane_vectors(self, start: int = None, window_size: int = None):
        data_key = f"{self.redis_prefix}:vectors:*"
        if start is not None and window_size is not None:
            data_key = f"{self.redis_prefix}:vectors:{start}:{window_size}"
        results = []
        for key in self.r.scan_iter(data_key):
            serialized = self.r.get(key)
            if serialized:
                data = pickle.loads(serialized)
                results.append(data)
        return results

    def set_target_threads(self, num_threads):
        data_key = f"{self.redis_prefix}:data:threads"
        self.r.set(data_key, num_threads)

    def get_target_threads(self):
        data_key = f"{self.redis_prefix}:data:threads"
        self.r.get(data_key)

    def clear(self):
        for key in self.r.scan_iter(f"{self.redis_prefix}:*"):
            self.r.delete(key)


if __name__ == '__main__':
    file_path = os.path.join(Path(__file__).parents[3], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, "vibrana:hydro-1-x")
    loader.load_numpy_file(False)
    res = loader.get_slice(0, 10_000)
    print(res)