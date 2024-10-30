import json
import math
import os
import re
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from matplotlib import colormaps
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

    colors = colormaps.get_cmap('turbo')(scores_norm)
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


def save_spectrogram_preview(data, save_path, sample_rate=20_000, window_size=2_000):
    w = np.repeat(1, window_size)
    SFT = ShortTimeFFT(w, hop=1, fs=sample_rate, mfft=None, scale_to="magnitude")
    Sx = SFT.spectrogram(data)
    Sx[Sx > np.percentile(Sx, 95)] = np.percentile(Sx, 95)
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(10, 3)
    ax.imshow(Sx, origin='lower', aspect='auto', extent=SFT.extent(len(data)), cmap='viridis')
    ax.get_xaxis().set_visible(False)
    plt.savefig(save_path, bbox_inches='tight', dpi=200)


def compute_time_varying_amplitude(values, window_size, sample_rate=20_000):
    w = np.repeat(1, window_size)
    SFT = ShortTimeFFT(w, hop=1, fs=sample_rate, mfft=window_size, scale_to='psd')
    Sx = SFT.stft(values)
    Sx = np.mean(abs(Sx), axis=0)
    return signal_variance(Sx, window_size=window_size)


def split_and_process_time_series(
        values: np.ndarray, timestamps: np.ndarray, events: np.ndarray,
        filename: str, prefix: str, dataset: str, subset: str,
        max_sample_size: int, projection_window_size: int, redis_client: Redis, limit: int = None):
    status = {}
    r_key = f"vibrana:{dataset}:{subset}:{filename}"
    if redis_client:
        status = json.loads(redis_client.get(r_key))

    base_target_path = os.path.join(Path(__file__).parents[1], "data", "chunks", dataset, subset)
    Path(base_target_path).mkdir(parents=True, exist_ok=True)

    event_indices = [find_nearest(timestamps, e) for e in events]
    name_index = 0
    existing_prefixes = [int(f.split("-")[-1]) for f in os.listdir(base_target_path) if f.startswith(prefix)]
    if len(existing_prefixes) > 0:
        name_index = max(existing_prefixes) + 1

    sample_rate = derive_sample_rate(timestamps)
    total = math.ceil(len(values) / max_sample_size)
    if redis_client:
        status["chunks"]["status"] = f"processing (0 / {total})"
        redis_client.set(r_key, json.dumps(status))

    needle = 0
    count = 0
    while needle < len(values):
        name = prefix + "-" + str(name_index + needle // max_sample_size).zfill(4)
        print(name)
        if redis_client:
            status["chunks"]["items"][name] = "splitting"
            redis_client.set(r_key, json.dumps(status))

        extracted = values[needle:needle + max_sample_size]
        extracted_ts = timestamps[needle:needle + max_sample_size]
        if len(extracted) <= projection_window_size:
            break
        os.mkdir(os.path.join(base_target_path, name))
        np.save(os.path.join(base_target_path, name, "values.npy"), extracted)
        np.save(os.path.join(base_target_path, name, "timestamps.npy"), extracted_ts)

        with open(os.path.join(base_target_path, name, "meta.json"), "w") as f:
            f.write(json.dumps({"original_file": filename, "machine": dataset, "position": needle}))

        window_events = [e - needle for e in event_indices if needle <= e <= needle + max_sample_size]
        np.save(os.path.join(base_target_path, name, "events.npy"), window_events)
        save_preview_image(extracted, os.path.join(base_target_path, name, "preview.png"))
        save_spectrogram_preview(extracted, os.path.join(base_target_path, name, "spectro.png"), window_size=projection_window_size, sample_rate=sample_rate)

        if redis_client:
            status["chunks"]["items"][name] = "projecting"
            redis_client.set(r_key, json.dumps(status))

        windows = sliding_window_view(extracted, window_shape=projection_window_size)
        projected = PCA(n_components=2).fit_transform(windows)
        np.save(os.path.join(base_target_path, name, "projected.npy"), projected)
        save_projection_preview_image(projected, os.path.join(base_target_path, name, "preview_projected.png"))

        if redis_client:
            status["chunks"]["items"][name] = "frequency"
            redis_client.set(r_key, json.dumps(status))
        freq = compute_time_varying_amplitude(extracted, projection_window_size, sample_rate)
        np.save(os.path.join(base_target_path, name, "freq.npy"), freq)

        if redis_client:
            status["chunks"]["items"][name] = "done"
            status["chunks"]["status"] = f"processing ({(needle // max_sample_size) + 1} / {total})"
            redis_client.set(r_key, json.dumps(status))
        needle += max_sample_size
        count += 1
        if limit is not None and count > limit:
            break


def process_subset(dataset: str, subset: str):
    dataset_path = os.path.join(Path(__file__).parents[1], "data", "parsed", dataset)
    chunk_path = os.path.join(Path(__file__).parents[1], "data", "chunks", dataset, subset)

    if os.path.exists(chunk_path):
        shutil.rmtree(chunk_path)
    Path(chunk_path).mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(os.path.join(dataset_path, subset)):
        for file in files:
            if not file.startswith("values") or not file.endswith(".npy"):
                continue
            values = np.load(os.path.join(root, file))
            timestamps = []
            if os.path.exists(os.path.join(root, "timestamps.npy")):
                timestamps = np.load(os.path.join(root, "timestamps.npy"))
            events = []
            if os.path.exists(os.path.join(root, "event_timestamps.npy")):
                events = np.load(os.path.join(root, "event_timestamps.npy"))
            print(os.path.join(root, file))
            prefix = re.sub(r"values-?|.npy", r"", file)
            if prefix == "":
                prefix = "signal"
            if dataset == "binder":
                prefix = "anomalous" if "gemischt" in root.lower() else "normal"
            split_and_process_time_series(values, timestamps, events, os.path.basename(root) + "/" + file, prefix, dataset, subset, 100_000, 2_000, None, 10)


def process_dataset(dataset: str):
    dataset_path = os.path.join(Path(__file__).parents[1], "data", "parsed", dataset)
    for subset in os.listdir(dataset_path):
        process_subset(dataset, subset)


if __name__ == '__main__':
    # process_dataset("hydro")
    process_dataset("binder")
