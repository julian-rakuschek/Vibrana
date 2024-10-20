import json
import math
import os
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from matplotlib import cm
from numpy.lib.stride_tricks import sliding_window_view
from redis import Redis
from scipy.signal import ShortTimeFFT
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

from parser.lib.util import find_nearest, derive_sample_rate, signal_variance


def save_projection_preview_image(data, save_path):
    scores = []
    for point in data:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    colors = cm.get_cmap('turbo')(scores_norm)
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(10, 10)
    ax.set_xlim([np.min(data[:, 0]), np.max(data[:, 0])])
    ax.set_ylim([np.min(data[:, 1]), np.max(data[:, 1])])
    ax.scatter(data[:, 0], data[:, 1], s=3, c=colors)
    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def save_preview_image(data, save_path):
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(10, 3)
    ax.plot(np.arange(len(data)), data, color="black")
    ax.set_xlim([0, len(data)])
    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def compute_time_varying_amplitude(values, timestamps, window_size, sample_rate=None):
    if sample_rate is None:
        sample_rate = derive_sample_rate(timestamps)
    w = np.repeat(1, window_size)
    SFT = ShortTimeFFT(w, hop=1, fs=sample_rate, mfft=window_size, scale_to='psd')
    Sx = SFT.stft(values)
    Sx = np.mean(abs(Sx), axis=0)
    return signal_variance(Sx, window_size=window_size)


def split_and_process_time_series(
        values: np.ndarray, timestamps: np.ndarray, events: np.ndarray,
        filename: str, prefix: str, machine: str,
        max_sample_size: int, projection_window_size: int, redis_client: Redis):
    status = {}
    r_key = f"vibrana:{machine}:{filename}"
    if redis_client:
        status = json.loads(redis_client.get(r_key))

    base_target_path = os.path.join(Path(__file__).parents[1], "data", "split", machine)
    Path(base_target_path).mkdir(parents=True, exist_ok=True)

    event_indices = [find_nearest(timestamps, e) for e in events]
    name_index = 0
    existing_prefixes = [int(f.split("-")[-1]) for f in os.listdir(base_target_path) if f.startswith(prefix)]
    if len(existing_prefixes) > 0:
        name_index = max(existing_prefixes) + 1

    sample_rate = derive_sample_rate(timestamps)
    total = math.ceil(len(values) / max_sample_size)
    if redis_client:
        status["split"]["status"] = f"processing (0 / {total})"
        redis_client.set(r_key, json.dumps(status))

    needle = 0
    while needle < len(values):
        name = prefix + "-" + str(name_index + needle // max_sample_size).zfill(4)
        print(name)
        if redis_client:
            status["split"]["items"][name] = "splitting"
            redis_client.set(r_key, json.dumps(status))

        extracted = values[needle:needle + max_sample_size]
        extracted_ts = timestamps[needle:needle + max_sample_size]
        os.mkdir(os.path.join(base_target_path, name))
        np.save(os.path.join(base_target_path, name, "values.npy"), extracted)
        np.save(os.path.join(base_target_path, name, "timestamps.npy"), extracted_ts)

        with open(os.path.join(base_target_path, name, "meta.json"), "w") as f:
            f.write(json.dumps({"original_file": filename, "machine": machine, "position": needle}))

        window_events = [e - needle for e in event_indices if needle <= e <= needle + max_sample_size]
        np.save(os.path.join(base_target_path, name, "events.npy"), window_events)
        save_preview_image(extracted, os.path.join(base_target_path, name, "preview.png"))


        if redis_client:
            status["split"]["items"][name] = "projecting"
            redis_client.set(r_key, json.dumps(status))

        windows = sliding_window_view(extracted, window_shape=projection_window_size)
        projected = PCA(n_components=2).fit_transform(windows)
        np.save(os.path.join(base_target_path, name, "projected.npy"), projected)
        save_projection_preview_image(projected, os.path.join(base_target_path, name, "preview_projected.png"))

        if redis_client:
            status["split"]["items"][name] = "frequency"
            redis_client.set(r_key, json.dumps(status))
        freq = compute_time_varying_amplitude(extracted, extracted_ts, projection_window_size, sample_rate)
        np.save(os.path.join(base_target_path, name, "freq.npy"), freq)

        if redis_client:
            status["split"]["items"][name] = "done"
            status["split"]["status"] = f"processing ({(needle // max_sample_size) + 1} / {total})"
            redis_client.set(r_key, json.dumps(status))
        needle += max_sample_size


