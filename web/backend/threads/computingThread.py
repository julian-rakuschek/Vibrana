import os
import threading
import time
import random
from pathlib import Path

import socketio
import redis
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA

from web.backend.data_loaders.dataLoaderBase import DataLoaderBase
from web.backend.data_loaders.redisLoader import RedisLoader


class ComputingThread(threading.Thread):
    def __init__(self, redis_instance: redis.Redis, dataLoader: DataLoaderBase, sliding_window_size: int, slice_size: int):
        threading.Thread.__init__(self)
        self.redis = redis_instance
        self.loader = dataLoader
        self.sliding_window_size = sliding_window_size
        self.slice_size = slice_size
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')
        time.sleep(0.5)
        self.sio.emit('join', {'room': dataLoader.redis_prefix})

    def compute_plane(self):
        next_index = random.randint(0, self.loader.data_size - self.slice_size)
        data = self.loader.get_slice(next_index, next_index + self.slice_size)
        windows = sliding_window_view(data, window_shape=self.sliding_window_size)
        projected = PCA(n_components=2).fit_transform(windows)
        v1, v2 = projected[:, 0], projected[:, 1]
        self.loader.store_hyperplane_vectors(v1, v2, next_index, self.slice_size)
        data = {"v1": v1.tolist(), "v2": v2.tolist(), "start_index": next_index, "slice_length": self.slice_size}
        self.sio.emit('share_computation_result', {'room': self.loader.redis_prefix, 'result': data})
        print(f"Computed vectors at {next_index}")

    def run(self):
        while True:
            if self.loader.get_target_threads() == 0 or self.loader.get_target_threads() is None:
                time.sleep(1)
                print("Inactive")
                continue
            self.compute_plane()


if __name__ == '__main__':
    file_path = os.path.join(Path(__file__).parents[2], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, "vibrana:hydro:x")
    loader.load_numpy_file(False)
    thread = ComputingThread(loader.r, loader, 1000, 10_000)
    thread.run()
    # thread.compute_plane()

