import json
import os.path
from pathlib import Path

import flask
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.manifold import MDS

analysis_app = flask.Blueprint("analysis", __name__)
samples_folder = os.path.join(Path(__file__).parents[3], "data", "samples")


@analysis_app.get("<machine>/<sampleId>/clustering")
def flask_get_clustering(machine, sampleId):
    window_size = flask.request.args.get("window_size", 1000)
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
