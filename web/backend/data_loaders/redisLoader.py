import datetime
import os
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import redis
from numpy.lib._stride_tricks_impl import sliding_window_view
from sklearn.decomposition import PCA
from tqdm import tqdm

from web.backend.data_loaders.dataLoaderBase import DataLoaderBase


class RedisLoader(DataLoaderBase):
    def __init__(self, path_to_npy, dataset, subset):
        super().__init__()
        self.path_to_npy = path_to_npy
        self.redis_prefix = f"vibrana:{dataset}:{subset}"
        self.dataset = dataset
        self.subset = subset
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
    file_path = os.path.join(Path(__file__).parents[3], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, "hydro", "x")
    loader.load_numpy_file()
    slice = loader.get_slice(0, 3_000)
    tde = sliding_window_view(slice, 300)
    points = PCA(n_components=2).fit_transform(tde)
    # plt.scatter(points[:, 0], points[:, 1], color="black")
    # plt.show()
    # print(points)
    with open("../../frontend/src/components/pages/landingPagePointCloud.ts", "w") as f:
        f.write("export const points: number[][] = " + str(points.tolist()))
    # loader.clear()