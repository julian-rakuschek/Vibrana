import os.path
import os.path
import random

import numpy as np
import stumpy
from numpy.lib.stride_tricks import sliding_window_view
from pymongo.database import Database
from scipy.spatial import distance
from tslearn.preprocessing import TimeSeriesResampler

from algorithms.lmds import landmark_MDS
from web.backend.settings import samples_folder


def compute_mds_embedding(sample_path, window_size):
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    windows = sliding_window_view(values, window_shape=window_size)
    lands = random.sample(range(0, windows.shape[0], 1), 50)
    lands = np.array(lands, dtype=int)
    Dl2 = distance.cdist(windows[lands, :], windows, 'chebyshev')
    xl_2 = landmark_MDS(Dl2, lands, 2)
    return xl_2


def compute_distance_profile(db: Database, machineId, sample_path):
    labels = list(db["labels"].find({"machine": machineId}))
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    distances = []
    extracted_label_values = []
    for label in labels:
        label_values: np.ndarray = np.load(os.path.join(samples_folder, label["machine"], label["sampleId"], "values.npy"))
        extracted_label_values.append(label_values[label["from"]:label["to"]])
    for label in extracted_label_values:
        d = stumpy.mass(label, values, normalize=True)
        d = TimeSeriesResampler(sz=len(values)).fit_transform(d.reshape(1, -1))[0, :, 0]
        distances.append(d)
    return np.min(np.array(distances), axis=0) if distances else []


def compute_normal_tube(db: Database, machineId):
    labels = list(db["labels"].find({"machine": machineId}))
    if len(labels) == 0:
        return [0, 0]

    normals = db["normals"].find_one({"machine": machineId})
    normals = [] if not normals else normals.get("samples")

    normal_min, normal_max = [], []
    for normal in normals:
        distances = compute_distance_profile(db, machineId, os.path.join(samples_folder, machineId, normal))
        normal_min.append(np.min(distances))
        normal_max.append(np.max(distances))
    normal_min = np.mean(normal_min)
    normal_max = np.mean(normal_max)
    return [normal_min, normal_max]


def count_anomaly_intervals(distances, normal_tube):
    found_anomalies = 0
    start = None
    length = 0
    for i, data_point in enumerate(distances):
        if data_point >= normal_tube[1]:
            if start is None:
                start = i
            length += 1
        elif start is not None:
            if length >= 100:
                found_anomalies += 1
            start = None
            length = 0
    if start is not None and length >= 100:
        found_anomalies += 1
    return found_anomalies


def reduce_distances(distances, n_segments):
    if n_segments >= len(distances):
        return distances
    window_size = len(distances) // n_segments
    distances_reduced = []
    for i in range(n_segments):
        subset = distances[i * window_size: (i + 1) * window_size]
        distances_reduced.append(float(np.min(subset)))
    return distances_reduced


def compute_anomaly_ratio(distances, normal_tube):
    below = (np.array(distances) <= normal_tube[0]).sum()
    return below / len(distances)


def compute_anomaly_metrics(db: Database, machineId, sampleId, normal_tube=None):
    labels = list(db["labels"].find({"machine": machineId}))
    sample_path = os.path.join(samples_folder, machineId, sampleId)
    distances = compute_distance_profile(db, machineId, sample_path)
    if normal_tube is None:
        normal_tube = compute_normal_tube(db, machineId)
    if len(labels) == 0:
        return None
    return {
        "machineId": machineId,
        "sampleId": sampleId,
        "distances_reduced": reduce_distances(distances, 100),
        "ratio": compute_anomaly_ratio(distances, normal_tube),
        "count": count_anomaly_intervals(distances, normal_tube)
    }
