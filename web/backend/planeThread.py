import os
import threading
import time
import random
from pathlib import Path

import redis
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA

from web.backend.data_loaders.dataLoaderBase import DataLoaderBase
from web.backend.data_loaders.redisLoader import RedisLoader


class PlaneThread(threading.Thread):
    def __init__(self, redis_instance: redis.Redis, dataLoader: DataLoaderBase, sliding_window_size: int, slice_size: int):
        threading.Thread.__init__(self)
        self.redis = redis_instance
        self.loader = dataLoader
        self.sliding_window_size = sliding_window_size
        self.slice_size = slice_size

    def compute_plane(self):
        next_index = random.randint(0, self.loader.data_size - self.slice_size)
        data = self.loader.get_slice(next_index, next_index + self.slice_size)
        windows = sliding_window_view(data, window_shape=self.sliding_window_size)
        projected = PCA(n_components=2).fit_transform(windows)
        v1, v2 = projected[:, 0], projected[:, 1]
        self.loader.store_hyperplane_vectors(v1, v2, next_index, self.slice_size)

    def run(self):
        while True:
            if self.loader.get_target_threads() == 0:
                time.sleep(1)
                continue
            self.compute_plane()


if __name__ == '__main__':
    file_path = os.path.join(Path(__file__).parents[2], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, "vibrana:hydro:x")
    loader.load_numpy_file(False)
    thread = PlaneThread(loader.r, loader, 1000, 10_000)
    thread.compute_plane()
    vectors = loader.retrieve_hyperplane_vectors()
    print(vectors)

