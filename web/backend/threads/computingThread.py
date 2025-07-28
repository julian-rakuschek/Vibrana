import datetime
import os
import threading
import time
import random
from collections.abc import Callable
from math import floor
from pathlib import Path

import numpy as np
import socketio
import redis
from numpy.lib.stride_tricks import sliding_window_view
from pymongo.synchronous.database import Database
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from web.backend.data_loaders.dataLoaderBase import DataLoaderBase
from web.backend.data_loaders.redisLoader import RedisLoader
import web.backend.helper.database as database

def compute_feature_descriptors(data, projected):
    feature_descriptors = {}

    radii = np.linalg.norm(projected, axis=1)
    counts, bins = np.histogram(radii, bins=20, range=(0, np.max(radii)), density=True)
    feature_descriptors["radii_distribution"] = {"bins": bins.tolist(), "counts": counts.tolist()}

    freqs = np.fft.rfftfreq(len(data))
    fft_values = np.fft.rfft(data)
    magnitude = np.abs(fft_values)
    counts, bins = np.histogram(freqs, bins=20, weights=magnitude)
    feature_descriptors["freq_distribution"] = {"bins": bins.tolist(), "counts": counts.tolist()}

    return feature_descriptors


class ComputingThread(threading.Thread):
    def __init__(self, db: Database, redis_instance: redis.Redis, dataLoader: RedisLoader, sliding_window_size: int, slice_size: int, insert_func: Callable, socket_client=None):
        threading.Thread.__init__(self)
        self.redis = redis_instance
        self.loader = dataLoader
        self.db = db
        self.sliding_window_size = sliding_window_size
        self.slice_size = slice_size
        self.sio = socket_client
        if self.sio is not None:
            self.sio.emit('join', {'room': dataLoader.redis_prefix})
        self.stop_request = False
        self.active = False
        self.insert_func = insert_func

    def compute_next_index(self):
        distribution = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)["weights"]
        if len(distribution["curve"]) == 0:
            return random.randint(0, self.loader.data_size - self.slice_size)

        x_values = np.array([e["x"] for e in distribution["curve"]])
        x_values = (x_values - np.min(x_values)) / (np.max(x_values) - np.min(x_values))
        y_values = np.array([e["y"] for e in distribution["curve"]])
        y_values = y_values / np.sum(y_values)
        cdf_values = np.cumsum(y_values)

        u = random.random()
        diffs = cdf_values - u
        left_side = np.copy(diffs)
        left_side[left_side > 0] = -np.inf
        left_idx = np.argmax(left_side)
        right_side = np.copy(diffs)
        right_side[right_side <= 0] = np.inf
        right_idx = np.argmin(right_side)

        random_index = x_values[left_idx] + (-left_side[left_idx] / (right_side[right_idx] - left_side[left_idx])) * (x_values[right_idx] - x_values[left_idx])
        random_index = floor(random_index * self.loader.data_size)
        return random_index

    def compute_plane(self):
        start = time.time()
        self.loader.load_numpy_file()
        next_index = self.compute_next_index()
        data = self.loader.get_slice(next_index, next_index + self.slice_size)
        windows = sliding_window_view(data, window_shape=self.sliding_window_size)
        windows = StandardScaler().fit_transform(windows)
        pca = PCA(n_components=2)
        pca.fit(windows)
        v1, v2 = pca.components_[0, :], pca.components_[1, :]
        projected = pca.transform(windows)
        feature_descriptors = compute_feature_descriptors(data, projected)
        to_insert = {
            "dataset": self.loader.dataset, "subset": self.loader.subset,
            "v1": v1.tolist(), "v2": v2.tolist(),
            "start_index": next_index, "slice_length": self.slice_size, "max_index": self.loader.data_size,
            "timestamp": datetime.datetime.now().timestamp(),
            "feature_descriptors": feature_descriptors
        }
        self.insert_func(self.loader.dataset, self.loader.subset, to_insert)
        if self.sio is not None:
            self.sio.emit('share_computation_result', {'room': self.loader.redis_prefix, 'result': database.serialize_mongodb(to_insert)})
        end = time.time()
        print(f"Computed vectors at {next_index} in {end - start} seconds")
        return database.serialize_mongodb(to_insert)

    def stop(self):
        self.stop_request = True

    def set_active(self, new_active):
        self.active = new_active

    def run(self):
        while True:
            if self.stop_request:
                break
            # if self.loader.get_target_threads() == 0 or self.loader.get_target_threads() is None:
            if not self.active:
                time.sleep(1)
                continue
            self.compute_plane()


if __name__ == '__main__':
    file_path = os.path.join(Path(__file__).parents[2], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, "hydro", "x")
    loader.load_numpy_file(False)
    db = database.get_db()
    thread = ComputingThread(db, loader.r, loader, 1000, 10_000)
    thread.compute_plane()
    # thread.start()
    # print("after run")
    # print(thread.is_alive())
    # time.sleep(3)
    # thread.stop()
    # thread.join()
    # print(thread.is_alive())
    # thread.compute_plane()
