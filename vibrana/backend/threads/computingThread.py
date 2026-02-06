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
from scipy import signal
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from vibrana.backend.data_loaders.dataLoaderBase import DataLoaderBase
from vibrana.backend.data_loaders.redisLoader import RedisLoader
import vibrana.backend.helper.database as database

def compute_feature_descriptors(data, projected, timestamps):
    feature_descriptors = {}

    radii = np.linalg.norm(projected, axis=1)
    counts, bins = np.histogram(radii, bins=20, range=(0, np.max(radii)), density=True)
    feature_descriptors["tde"] = {"bins": bins.tolist(), "counts": counts.tolist()}

    fs = 1.0 / np.median(np.diff(timestamps))
    f, Pxx_spec = signal.welch(data, fs, scaling='spectrum')
    feature_descriptors["psd"] = {"f": f.tolist(), "Pxx_spec": Pxx_spec.tolist()}

    return feature_descriptors


def compute_pca(data, sliding_window_size):
    norm = np.max(np.abs(data))
    windows = sliding_window_view(data / norm, window_shape=sliding_window_size)
    windows = StandardScaler().fit_transform(windows)
    pca = PCA(n_components=2)
    pca.fit(windows)
    v1, v2 = pca.components_[0, :], pca.components_[1, :]
    projected = pca.transform(windows)
    return v1, v2, projected


class ComputingThread(threading.Thread):
    def __init__(self, db: Database, redis_instance: redis.Redis, dataLoader: RedisLoader, insert_func: Callable, socket_client=None):
        threading.Thread.__init__(self)
        self.redis = redis_instance
        self.loader = dataLoader
        self.db = db
        self.sio = socket_client
        if self.sio is not None:
            self.sio.emit('join', {'room': dataLoader.redis_prefix})
        self.stop_request = False
        self.active = False
        self.insert_func = insert_func

    def sample_next_index(self):
        params = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)["sampling"]
        intervals = params.get("intervals", [])
        if len(intervals) == 0:
            return floor(random.random() * self.loader.data_size)
        lengths = [abs(end - start) for start, end in intervals]
        total_length = sum(lengths)
        r = random.uniform(0, total_length)
        cumulative = 0
        for (start, end), length in zip(intervals, lengths):
            if cumulative + length >= r:
                return floor((start + (r - cumulative)) * self.loader.data_size)
            cumulative += length
        return 0

    def process_slice(self):
        start = time.time()
        self.loader.load_numpy_file()
        next_index = self.sample_next_index()
        params = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)
        slice_size = params["sampling"]["slice_size"]
        sliding_window_size = params["tde"]["sliding_window_size"]
        data = self.loader.get_slice(next_index, next_index + slice_size)
        timestamps = self.loader.get_slice(next_index, next_index + slice_size, timestamps=True)
        if sliding_window_size >= len(data):
            return
        v1, v2, projected = compute_pca(data, sliding_window_size)
        feature_descriptors = compute_feature_descriptors(data, projected, timestamps)

        to_insert = {
            "dataset": self.loader.dataset, "subset": self.loader.subset,
            "v1": v1.tolist(), "v2": v2.tolist(), "sliding_window_size": sliding_window_size,
            "start_index": next_index, "slice_length": slice_size, "max_index": self.loader.data_size,
            "timestamp": datetime.datetime.now().timestamp(),
            "feature_descriptors": feature_descriptors
        }

        labels = self.insert_func(self.loader.dataset, self.loader.subset, to_insert)
        latest = self.db["fingerprints"].find().sort({"$natural": -1}).limit(1)[0]

        if self.sio is not None:
            self.sio.emit('share_computation_result', {
                'room': self.loader.redis_prefix,
                'new_fingerprint': database.serialize_mongodb(latest),
                'labels': labels
            })
        end = time.time()
        print(f"Processed slice at {next_index} in {end - start} seconds")
        return {'new_fingerprint': database.serialize_mongodb(latest), 'labels': labels}




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
            self.process_slice()


if __name__ == '__main__':
    dataset = "hydro"
    subset = "x"
    file_path = os.path.join(Path(__file__).parents[2], "data", "parsed", "hydro", "hydro-1", "values-hydro-1-x.npy")
    loader = RedisLoader(file_path, dataset, subset)
    loader.load_numpy_file(False)
    db = database.get_db()
    insert_func = lambda dataset, subset, data: database.store_fingerprint(db, data, dataset, subset)
    thread = ComputingThread(db, loader.r, loader, insert_func)
    thread.process_slice()
    # thread.start()
    # print("after run")
    # print(thread.is_alive())
    # time.sleep(3)
    # thread.stop()
    # thread.join()
    # print(thread.is_alive())
    # thread.compute_plane()
