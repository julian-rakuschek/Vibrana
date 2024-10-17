import json
import math
import os
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from redis import Redis
from scipy.signal import ShortTimeFFT
from sklearn.decomposition import PCA

from parser.util import find_nearest, derive_sample_rate, signal_variance


def save_preview_image(data, save_path):
    plt.clf()
    formatter = plticker.FuncFormatter(lambda x_val, tick_pos: f"{x_val}")
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(10, 3)
    ax.plot(np.arange(len(data)), data, color="black")
    ax.set_xlim([0, len(data)])
    ax.xaxis.set_major_formatter(formatter)
    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def compute_time_varying_amplitude(values, timestamps):
    w = np.repeat(1, 1000)
    SFT = ShortTimeFFT(w, hop=1, fs=derive_sample_rate(timestamps), mfft=1000, scale_to='psd')
    Sx = SFT.stft(values)
    Sx = np.mean(abs(Sx), axis=0)
    return signal_variance(Sx, window_size=1000)



def process_experiment(folder, target_folder, sample_prefix="", override=True):
    base_path = os.path.join(Path(__file__).parents[1], "data", folder)
    folder_values = np.load(os.path.join(base_path, "values.npy"))
    folder_values = folder_values[80_000:950_000]
    folder_events = np.load(os.path.join(base_path, "event_timestamps.npy"))
    folder_timestamps = np.load(os.path.join(base_path, "timestamps.npy"))
    folder_timestamps = folder_timestamps[80_000:950_000]
    event_indices = [find_nearest(folder_timestamps, e) for e in folder_events]

    print(folder)
    print("Target", target_folder)
    print("Total ts length:", len(folder_values))

    if os.path.exists(target_folder) and override:
        shutil.rmtree(target_folder)
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)

    window_size = 100_000
    needle = 0
    while needle < len(folder_values):
        name = sample_prefix + str(needle // window_size).zfill(4)
        print(name)
        extracted = folder_values[needle:needle+window_size]
        os.mkdir(os.path.join(target_folder, name))
        np.save(os.path.join(target_folder, name, "values.npy"), extracted)
        window_events = [e - needle for e in event_indices if needle <= e <= needle + window_size]
        np.save(os.path.join(target_folder, name, "events.npy"), window_events)
        save_preview_image(extracted, os.path.join(target_folder, name, "preview.png"))
        windows = sliding_window_view(extracted, window_shape=2000)
        projected = PCA(n_components=2).fit_transform(windows)
        np.save(os.path.join(target_folder, name, "projected.npy"), projected)
        needle += window_size


def example1():
    abnormal_ = "5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt"  # abnormal
    normal_ = "5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde"  # normal
    base_target_path = os.path.join(Path(__file__).parents[1], "data", "samples")
    if not os.path.exists(base_target_path):
        os.makedirs(base_target_path)
    process_experiment(abnormal_, os.path.join(base_target_path, "5-10-1t-10-16"), "abnormal-", override=True)
    process_experiment(normal_, os.path.join(base_target_path, "5-10-1t-10-16"), "normal-", override=False)


def example2():
    abnormal_ = "16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde gemischt 31,5-62" # interesting-curve
    normal_ = "16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde" # interesting-curve
    base_target_path = os.path.join(Path(__file__).parents[1], "data", "samples")
    if not os.path.exists(base_target_path):
        os.makedirs(base_target_path)
    process_experiment(abnormal_, os.path.join(base_target_path, "interesting-curve"), "abnormal-", override=True)
    process_experiment(normal_, os.path.join(base_target_path, "interesting-curve"), "normal-", override=False)


def split_and_process_time_series(
        values: np.ndarray, timestamps: np.ndarray, events: np.ndarray,
        filename: str, prefix: str, machine: str,
        max_sample_size: int, redis_client: Redis):
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

    total = math.ceil(len(values) / max_sample_size)
    if redis_client:
        status["split"]["status"] = f"processing (0 / {total})"
        redis_client.set(r_key, json.dumps(status))

    needle = 0
    while needle < len(values):
        name = prefix + "-" + str(name_index + needle // max_sample_size).zfill(4)

        if redis_client:
            status["split"]["items"][name] = "splitting"
            redis_client.set(r_key, json.dumps(status))

        extracted = values[needle:needle + max_sample_size]
        extracted_ts = timestamps[needle:needle + max_sample_size]
        os.mkdir(os.path.join(base_target_path, name))
        np.save(os.path.join(base_target_path, name, "values.npy"), extracted)
        window_events = [e - needle for e in event_indices if needle <= e <= needle + max_sample_size]
        np.save(os.path.join(base_target_path, name, "events.npy"), window_events)
        save_preview_image(extracted, os.path.join(base_target_path, name, "preview.png"))

        if redis_client:
            status["split"]["items"][name] = "projecting"
            redis_client.set(r_key, json.dumps(status))

        windows = sliding_window_view(extracted, window_shape=2000)
        projected = PCA(n_components=2).fit_transform(windows)
        np.save(os.path.join(base_target_path, name, "projected.npy"), projected)

        if redis_client:
            status["split"]["items"][name] = "frequency"
            redis_client.set(r_key, json.dumps(status))
        freq = compute_time_varying_amplitude(extracted, extracted_ts)
        np.save(os.path.join(base_target_path, name, "freq.npy"), freq)

        if redis_client:
            status["split"]["items"][name] = "done"
            status["split"]["status"] = f"processing ({needle // max_sample_size} / {total})"
            redis_client.set(r_key, json.dumps(status))
        needle += max_sample_size


if __name__ == '__main__':
    example1()
    example2()