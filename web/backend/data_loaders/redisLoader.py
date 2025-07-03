import datetime
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
        self.set_target_threads(0)

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

    def get_slice(self, start_index=0, end_index=-1, as_numpy=True):
        self.load_numpy_file()
        data_key = f"{self.redis_prefix}:data"
        retrieved = self.r.lrange(data_key, start_index, end_index)
        retrieved = [float(x) for x in retrieved]
        if as_numpy:
            retrieved = np.array(retrieved)
        return retrieved

    def store_hyperplane_vectors(self, v1: np.ndarray, v2: np.ndarray, start_index: int, slice_length: int):
        data_key = f"{self.redis_prefix}:vectors:{start_index}:{slice_length}"
        data = {"v1": v1.tolist(), "v2": v2.tolist(), "start_index": start_index, "slice_length": slice_length, "timestamp": datetime.datetime.now().timestamp()}
        serialized = pickle.dumps(data)
        self.r.set(data_key, serialized)

    def retrieve_hyperplane_vectors(self, start_index: int = None, slice_length: int = None, exclude_vector_data: bool = False):
        data_key = f"{self.redis_prefix}:vectors:*"
        if start_index is not None and slice_length is not None:
            data_key = f"{self.redis_prefix}:vectors:{start_index}:{slice_length}"
        results = []
        for key in self.r.scan_iter(data_key):
            serialized = self.r.get(key)
            if serialized:
                data = pickle.loads(serialized)
                if exclude_vector_data:
                    data = {"slice_length": data["slice_length"], "start_index": data["start_index"]}
                results.append(data)
        return results

    def set_target_threads(self, num_threads):
        data_key = f"{self.redis_prefix}:data:threads"
        self.r.set(data_key, str(num_threads))

    def get_target_threads(self):
        data_key = f"{self.redis_prefix}:data:threads"
        value = self.r.get(data_key)
        return int(value) if value else None

    def clear(self):
        for key in self.r.scan_iter(f"{self.redis_prefix}:*"):
            self.r.delete(key)


if __name__ == '__main__':
    file_path = os.path.join(Path(__file__).parents[3], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, "vibrana:hydro:x")
    loader.clear()
    # loader.clear()
    # loader.load_numpy_file(False)
    # res = loader.get_slice(0, 10_000)
    # print(res)
    print(loader.get_target_threads())
    loader.set_target_threads(1)
    print(loader.get_target_threads())
