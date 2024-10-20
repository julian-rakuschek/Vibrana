import json
import os
from math import floor
from pathlib import Path
from typing import List

import numpy as np
import stumpy
from matplotlib import pyplot as plt

from parser.dwparser import process_file
from parser.extract_snippets import split_and_process_time_series
from parser.lib.util import find_nearest

data_folder = os.path.join(Path(__file__).parents[1], "data", "raw")
parsed_folder = os.path.join(Path(__file__).parents[1], "data", "parsed")
split_folder = os.path.join(Path(__file__).parents[1], "data", "split")


def parse_folder(
        folder: str, window_size: int = 2000,
        compute_matrix_profile: bool = True, max_sample_size: int = 100_000,
        plots_to_save: List[str] = None, prefix: str = "signal", prefix_ground_truth: bool = False,
        cutoff_ratio: float = 0.2
):
    if plots_to_save is None:
        plots_to_save = ["plain", "fluss"]
    folder_path = os.path.join(data_folder, folder)
    if not os.path.exists(folder_path):
        raise Exception(f"{folder_path} does not exist")

    all_values = []
    cuts = []

    for file in os.listdir(folder_path):
        print(file)
        if not file.endswith("dxd"):
            continue
        values, timestamps, events = process_file(os.path.join(folder_path, file))
        event_indices = [find_nearest(timestamps, e) for e in events]

        if cutoff_ratio is not None and 0 < cutoff_ratio < 0.5:
            cut_index = floor(len(values) * cutoff_ratio)
            values = values[cut_index:len(values) - cut_index]
            timestamps = timestamps[cut_index:len(values) - cut_index]

        all_values.append(values)
        cuts.append(sum(cuts) + len(values))

        file_parsed_folder = os.path.join(parsed_folder, folder, file.replace(".dxd", ""))
        Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)
        np.save(os.path.join(file_parsed_folder, "values.npy"), values)
        np.save(os.path.join(file_parsed_folder, "timestamps.npy"), timestamps)
        np.save(os.path.join(file_parsed_folder, "event_timestamps.npy"), np.array(events))

        if "plain" in plots_to_save:
            plt.clf()
            plt.figure(figsize=(50, 10))
            plt.axis('off')
            plt.plot(values, color="black")
            plt.vlines(event_indices, np.min(values), np.max(values), color="r")
            plt.savefig(os.path.join(file_parsed_folder, "plot.png"), bbox_inches='tight')
        if prefix_ground_truth:
            prefix = "anomalous" if "gemischt" in file.lower() else "normal"
        split_and_process_time_series(values, timestamps, events, file, prefix, folder, max_sample_size, window_size, None)

    if not compute_matrix_profile:
        return
    print("computing matrix profile")
    values = np.concatenate(all_values, axis=0)
    mat = stumpy.gpu_stump(values, window_size)
    np.save(os.path.join(parsed_folder, f"mat-profile-{folder}.npy"), values)
    if len(all_values) >= 2:
        cac, regime_locs = stumpy.fluss(mat[:, 1], window_size, len(all_values))
        with open(f"mat-profile-fuss-{folder}.json", "w") as f:
            f.write(json.dumps({"cuts": cuts, "regime_locs": regime_locs}))
        if "fluss" in plots_to_save:
            plt.clf()
            fig, ax = plt.subplots(nrows=2, ncols=1)
            fig.set_size_inches((100, 20))

            ax[0].plot(np.arange(len(values)), values, color="black")
            ax[1].plot(np.arange(len(mat)), mat, color="black")

            ax[0].set_title("Values with FLUSS Segmentation", fontsize=20)
            ax[1].set_title("Matrix profile of combined signal", fontsize=20)

            ax[0].vlines(regime_locs, 0, np.max(values), color="#ff4d4d", linewidth=1)
            ax[0].vlines(cuts, 0, np.max(values), color="navy", linewidth=1)
            ax[1].vlines(regime_locs, 0, np.max(values), color="#ff4d4d", linewidth=1)
            ax[1].vlines(cuts, 0, np.max(values), color="navy", linewidth=1)
            plt.savefig(os.path.join(parsed_folder, f"mat-profile-fluss-{folder}.png"), bbox_inches='tight', dpi=200)


if __name__ == '__main__':
    parse_folder("5-10-1t-10-16", prefix_ground_truth=True)
