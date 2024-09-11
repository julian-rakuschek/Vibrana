import json
import os.path
from pathlib import Path
import random

import flask
import numpy as np
import stumpy
from numpy.lib.stride_tricks import sliding_window_view
from scipy.spatial import distance
from sklearn.manifold import MDS

from algorithms.lmds import landmark_MDS
from web.backend.modules.database import get_db, flask_get_normals

analysis_app = flask.Blueprint("analysis", __name__)
samples_folder = os.path.join(Path(__file__).parents[3], "data", "samples")


@analysis_app.get("<machine>/<sampleId>/clustering_old")
def flask_get_clustering(machine, sampleId):
    window_size = int(flask.request.args.get("window_size", 1000))
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    windows = sliding_window_view(values, window_shape=window_size)[::window_size]
    ffts = [np.fft.fft(w) for w in windows]
    distances = [[np.linalg.norm(ffts[i] - ffts[j]) for j in range(len(windows))] for i in range(len(windows))]
    embedding: np.ndarray = MDS(dissimilarity="precomputed").fit_transform(distances)
    return embedding.tolist()


@analysis_app.get("<machine>/<sampleId>/clustering")
def flask_get_clustering2(machine, sampleId):
    window_size = int(flask.request.args.get("window_size", 1000))
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    windows = sliding_window_view(values, window_shape=window_size)
    lands = random.sample(range(0, windows.shape[0], 1), 50)
    lands = np.array(lands, dtype=int)
    Dl2 = distance.cdist(windows[lands, :], windows, 'chebyshev')
    xl_2 = landmark_MDS(Dl2, lands, 2)
    return xl_2.tolist()


@analysis_app.get("<machine>/<sampleId>/similarities")
def flask_get_similarities(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    labels = list(get_db()["labels"].find({"machine": machine}))
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    similarities = []
    for label in labels:
        d = stumpy.mass(values[label["from"]:label["to"]], values, normalize=False)
        d[d < 10] = np.mean(d)
        similarities.append(d)
    if not similarities:
        return []
    similarities = np.max(np.array(similarities), axis=0)
    print(np.array(similarities))
    return similarities.tolist()


@analysis_app.get("<machine>/normal_band")
def flask_get_normal_tube(machine):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    normals = flask_get_normals(machine)
    normal_min, normal_max = [], []
    for normal in normals:
        similarities = flask_get_similarities(machine, normal)
        normal_min.append(np.min(similarities))
        normal_max.append(np.max(similarities))
    normal_min = np.mean(normal_min)
    normal_max = np.mean(normal_max)
    return [normal_min, normal_max]
