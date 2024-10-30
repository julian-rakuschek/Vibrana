import os.path
import os.path
import random

import numpy as np
import stumpy
from numpy.lib.stride_tricks import sliding_window_view
from pymongo.database import Database
from scipy.spatial import distance
from tslearn.preprocessing import TimeSeriesResampler

from web.backend.helper.lmds import landmark_MDS
from web.backend.settings import chunks_folder


def compute_mds_embedding(sample_path, window_size):
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    windows = sliding_window_view(values, window_shape=window_size)
    lands = random.sample(range(0, windows.shape[0], 1), 100)
    lands = np.array(lands, dtype=int)
    Dl2 = distance.cdist(windows[lands, :], windows, 'sqeuclidean')
    xl_2 = landmark_MDS(Dl2, lands, 2)
    return xl_2


def compute_distance_profile(sample_path, labels):
    if not os.path.exists(os.path.join(sample_path, "values.npy")):
        return []
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    distances = []
    extracted_label_values = []
    for label in labels:
        label_path = os.path.join(chunks_folder, label["dataset"], label["chunks"], "values.npy")
        if not os.path.exists(label_path):
            continue
        label_values: np.ndarray = np.load(label_path)
        extracted_label_values.append(label_values[label["from"]:label["to"]])
    for label in extracted_label_values:
        if len(label) > len(values):
            continue
        d = stumpy.mass(label, values, normalize=True)
        d = TimeSeriesResampler(sz=len(values)).fit_transform(d.reshape(1, -1))[0, :, 0]
        distances.append(d)
    return np.min(np.array(distances), axis=0) if len(distances) > 0 else []


def compute_normal_tube(dataset, subset, labels, normals):
    if len(labels) == 0:
        return [0, 0]

    normals = [] if not normals else normals.get("chunks")
    normal_min, normal_max = [], []
    for normal in normals:
        distances = compute_distance_profile(os.path.join(chunks_folder, dataset, subset, normal), labels)
        if len(distances) == 0:
            continue
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
        if data_point <= normal_tube[0] or data_point >= normal_tube[1]:
            if start is None:
                start = i
            length += 1
        elif start is not None:
            found_anomalies += 1
            start = None
            length = 0
    if start is not None:
        found_anomalies += 1
    return found_anomalies


def reduce_distances(distances, normal_tube, n_segments, keep_original_length=False):
    if n_segments >= len(distances):
        return distances
    window_size = len(distances) // n_segments
    remainder = len(distances) % n_segments
    distances_reduced = []
    for i in range(n_segments):
        subset = distances[i * window_size: (i + 1) * window_size]
        if np.any(subset < normal_tube[0]):
            if keep_original_length:
                distances_reduced.extend(list(np.repeat(np.min(subset), window_size)))
            else:
                distances_reduced.append(float(np.min(subset)))
        else:
            if keep_original_length:
                distances_reduced.extend(list(np.repeat(np.mean(subset), window_size)))
            else:
                distances_reduced.append(float(np.mean(subset)))
    if keep_original_length:
        subset = distances[-remainder:]
        if np.any(subset < normal_tube[0]):
            distances_reduced.extend(list(np.repeat(np.min(subset), remainder)))
        else:
            distances_reduced.extend(list(np.repeat(np.mean(subset), remainder)))
    return distances_reduced


def compute_anomaly_ratio(distances, normal_tube):
    below = (np.array(distances) <= normal_tube[0]).sum()
    if len(distances) == 0:
        return 0
    return below / len(distances)


def compute_anomaly_metrics(dataset, subset, chunk, labels, normals, normal_tube=None):
    sample_path = os.path.join(chunks_folder, dataset, subset)
    distances = compute_distance_profile(sample_path, labels)
    if normal_tube is None:
        normal_tube = compute_normal_tube(dataset, subset, labels, normals)
    if len(labels) == 0:
        return None
    return {
        "dataset": dataset,
        "subset": subset,
        "chunk": chunk,
        "distances_reduced": reduce_distances(distances, normal_tube, 200),
        "ratio": compute_anomaly_ratio(distances, normal_tube),
        "count": count_anomaly_intervals(distances, normal_tube)
    }


def compute_quantized_distance_profile(dataset, subset, chunk, labels, normals):
    chunk_path = os.path.join(chunks_folder, dataset, subset, chunk)
    distances = compute_distance_profile(chunk_path, labels)
    normal_tube = compute_normal_tube(dataset, subset, labels, normals)
    return reduce_distances(distances, normal_tube, 1000, True)
