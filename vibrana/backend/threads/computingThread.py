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

from vibrana.backend.data_loaders.dataLoaderBase import DataLoaderBase
from vibrana.backend.data_loaders.redisLoader import RedisLoader
import vibrana.backend.helper.database as database

fft_BINS = 50


def bin_fft(frequencies, magnitudes, bins=fft_BINS):
    if len(magnitudes) <= bins:
        return frequencies, magnitudes
    frequency_bins = np.array_split(frequencies, bins)
    power_bins = np.array_split(magnitudes, bins)
    return (
        np.array([np.mean(bin_values) for bin_values in frequency_bins]),
        np.array([np.max(bin_values) for bin_values in power_bins]),
    )


def compute_feature_descriptors(data, projected, sample_rate=1.0):
    feature_descriptors = {}

    radii = np.linalg.norm(projected, axis=1)
    counts, bins = np.histogram(radii, bins=20, range=(0, np.max(radii)), density=True)
    feature_descriptors["tde"] = {"bins": bins.tolist(), "counts": counts.tolist()}

    fft_frequency_bins = np.fft.rfftfreq(len(data), d=1.0 / sample_rate)
    fft_magnitudes = np.abs(np.fft.rfft(data))
    binned_frequency_bins, binned_fft_magnitudes = bin_fft(fft_frequency_bins, fft_magnitudes)
    feature_descriptors["fft"] = {"f": binned_frequency_bins.tolist(), "magnitudes": binned_fft_magnitudes.tolist()}

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
    def __init__(self, db: Database, dataLoader: RedisLoader, insert_func: Callable, socket_client=None):
        threading.Thread.__init__(self)
        self.loader = dataLoader
        self.db = db
        self.sio = socket_client
        if self.sio is not None:
            self.sio.emit('join', {'room': dataLoader.redis_prefix})
        self.stop_request = False
        self.active = False
        self.insert_func = insert_func

    def get_fingerprints_in_intervals(self, intervals, all_fingerprints):
        fingerprints = []
        for interval in intervals:
            interval_start = int(interval[0] * self.loader.data_size)
            interval_end = int(interval[1] * self.loader.data_size)

            fingerprints.extend([
                fp for fp in all_fingerprints
                if fp["start_index"] < interval_end
                   and fp["start_index"] + fp["slice_length"] > interval_start
            ])
        return fingerprints

    def sample_random(self):
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


    def sample_binary(self):
        params = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)["sampling"]
        fingerprints = database.get_fingerpints_for_sampling(self.db, self.loader.dataset, self.loader.subset)
        intervals = params.get("intervals", [])
        if len(intervals) > 0:
            fingerprints = self.get_fingerprints_in_intervals(intervals, fingerprints)
        if len(fingerprints) < 2:
            return self.sample_random()
        gaps = []
        current_label_tde = fingerprints[0]["label"]["tde"]
        current_label_fft = fingerprints[0]["label"]["fft"]
        for i in range(len(fingerprints) - 1):
            if current_label_tde != fingerprints[i + 1]["label"]["tde"]:
                gaps.append([fingerprints[i]["start_index"], fingerprints[i + 1]["start_index"]])
                current_label_tde = fingerprints[i + 1]["label"]["tde"]
            if current_label_fft != fingerprints[i + 1]["label"]["fft"]:
                gaps.append([fingerprints[i]["start_index"], fingerprints[i + 1]["start_index"]])
                current_label_fft = fingerprints[i + 1]["label"]["fft"]
        sorted_gaps = sorted(gaps, key=lambda x: abs(x[0] - x[1]), reverse=True)
        if len(sorted_gaps) == 0:
            return self.sample_random()
        return int(np.mean(sorted_gaps[0]))

    def sample_largest_gap(self):
        params = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)["sampling"]
        fingerprints = database.get_fingerpints_for_sampling(self.db, self.loader.dataset, self.loader.subset)
        intervals = params.get("intervals", [])
        if len(intervals) > 0:
            fingerprints = self.get_fingerprints_in_intervals(intervals, fingerprints)
        if len(fingerprints) == 0:
            return self.loader.data_size // 2
        fingerprints = sorted(fingerprints, key=lambda x: x["start_index"])
        gaps = []
        gaps.append([0, fingerprints[0]["start_index"]])
        for i in range(len(fingerprints) - 1):
            gaps.append([fingerprints[i]["start_index"], fingerprints[i + 1]["start_index"]])
        gaps.append([fingerprints[-1]["start_index"], self.loader.data_size])
        sorted_gaps = sorted(gaps, key=lambda x: abs(x[0] - x[1]), reverse=True)
        if len(sorted_gaps) == 0:
            return self.sample_random()
        return int(np.mean(sorted_gaps[0]))

    def linear_sample(self):
        def overlaps(candidate_start, candidate_end, fp):
            fp_start = fp["start_index"]
            fp_end = fp_start + fp["slice_length"]
            return candidate_start < fp_end and fp_start < candidate_end

        def scan_range(start_index, end_index_exclusive, fingerprints, slice_size):
            max_start = end_index_exclusive - slice_size
            needle = start_index
            while needle <= max_start:
                candidate_end = needle + slice_size
                if not any(overlaps(needle, candidate_end, fp) for fp in fingerprints):
                    return needle
                needle += slice_size
            return None

        params = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)["sampling"]
        slice_size = params["slice_size"]
        intervals = params.get("intervals", [])
        all_fingerprints = database.get_fingerpints_for_sampling(
            self.db, self.loader.dataset, self.loader.subset
        )

        if not intervals:
            result = scan_range(0, self.loader.data_size, all_fingerprints, slice_size)
            return result if result is not None else self.sample_random()

        for interval in intervals:
            interval_start = int(interval[0] * self.loader.data_size)
            interval_end = int(interval[1] * self.loader.data_size)

            interval_fingerprints = [
                fp for fp in all_fingerprints
                if fp["start_index"] < interval_end
                   and fp["start_index"] + fp["slice_length"] > interval_start
            ]

            result = scan_range(interval_start, interval_end, interval_fingerprints, slice_size)
            if result is not None:
                return result

        return self.sample_random()


    def process_slice(self):
        start = time.time()
        self.loader.load_numpy_file()
        params = database.get_parameters(self.db, self.loader.dataset, self.loader.subset)
        if params["sampling"]["samplingAlgorithm"] == "random":
            next_index = self.sample_random()
        elif params["sampling"]["samplingAlgorithm"] == "binary":
            next_index = self.sample_binary()
        elif params["sampling"]["samplingAlgorithm"] == "gaps":
            next_index = self.sample_largest_gap()
        elif params["sampling"]["samplingAlgorithm"] == "linear":
            next_index = self.linear_sample()
        else:
            next_index = self.sample_random()
        slice_size = params["sampling"]["slice_size"]
        sliding_window_size = params["tde"]["sliding_window_size"]
        data = self.loader.get_slice(next_index, next_index + slice_size, as_numpy=True)
        if sliding_window_size >= len(data):
            return
        v1, v2, projected = compute_pca(data, sliding_window_size)
        feature_descriptors = compute_feature_descriptors(data, projected, self.loader.fs)

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
    file_path = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", "hydro", "x", "values.npy")
    loader = RedisLoader(file_path, dataset, subset)
    loader.load_numpy_file(False)
    db = database.get_db()
    insert_func = lambda dataset, subset, data: database.store_fingerprint(db, data, dataset, subset)
    thread = ComputingThread(db, loader, insert_func)
    res = thread.sample_largest_gap()
    print(res)
    # thread.start()
    # print("after run")
    # print(thread.is_alive())
    # time.sleep(3)
    # thread.stop()
    # thread.join()
    # print(thread.is_alive())
    # thread.compute_plane()
