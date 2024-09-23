import os
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA

from util import find_nearest


def save_preview_image(data, save_path):
    plt.clf()
    formatter = plticker.FuncFormatter(lambda x_val, tick_pos: f"{x_val}")
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(30, 10)
    ax.plot(np.arange(len(data)), data, color="black")
    ax.set_xlim([0, len(data)])
    ax.xaxis.set_major_formatter(formatter)
    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


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


if __name__ == '__main__':
    example2()