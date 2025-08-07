import os.path
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt



def extract_slice(raw_file_path, start, end):
    df = pd.read_parquet(raw_file_path, engine='fastparquet')
    channels = ["Ch1", "Ch2", "Ch3"]
    data = []
    for c in channels:
        channel_data = df[[c]].to_numpy().flatten()[start:end]
        channel_mean = np.mean(channel_data)

        if c == "Ch1":
            channel_data[channel_data > 0.5] = channel_mean
        if c == "Ch2":
            channel_data[channel_data > 100] = channel_mean
            channel_mean = np.mean(channel_data)
            channel_data[channel_data > 0.15] = channel_mean
        if c == "Ch3":
            channel_data[channel_data < 8] = channel_mean

        data.append(channel_data)
    return data


def save_preview_image(Ch1, Ch2, Ch3, save_path):
    plt.clf()
    fig, ax = plt.subplots(nrows=3, ncols=1)
    fig.set_size_inches(50, 30)

    ax[0].set_title("Channel 1", fontsize=20)
    ax[0].set_xlim([0, len(Ch1)])
    ax[0].plot(Ch1, color="black")

    ax[1].set_title("Channel 2", fontsize=20)
    ax[1].set_xlim([0, len(Ch2)])
    ax[1].plot(Ch2, color="black")

    ax[2].set_title("Channel 3", fontsize=20)
    ax[2].set_xlim([0, len(Ch3)])
    ax[2].plot(Ch3, color="black")

    plt.savefig(save_path, bbox_inches='tight')


def parse_hydro(source_file_name, target_folder_name):
    raw_file_path = os.path.join(Path(__file__).parents[2], "data", "raw-signals", "hydro", source_file_name)
    file_parsed_folder = os.path.join(Path(__file__).parents[2], "data", "prepared-signals", "streams", target_folder_name)
    clipboard_folder = os.path.join(Path(__file__).parents[2], "data", "clipboard", "hydro")

    channel_folder = [
        os.path.join(file_parsed_folder, "x"),
        os.path.join(file_parsed_folder, "y"),
        os.path.join(file_parsed_folder, "z")
    ]

    if not os.path.exists(raw_file_path):
        print(f"Could not find {raw_file_path}")
        return
    shutil.rmtree(file_parsed_folder, ignore_errors=True)
    shutil.rmtree(clipboard_folder, ignore_errors=True)
    Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)
    Path(clipboard_folder).mkdir(parents=True, exist_ok=True)
    for folder in channel_folder:
        Path(folder).mkdir(parents=True, exist_ok=True)

    values = extract_slice(raw_file_path, 68_500_000, 72_500_000)
    np.save(os.path.join(channel_folder[0], f"values.npy"), values[0])
    np.save(os.path.join(channel_folder[1], f"values.npy"), values[1])
    np.save(os.path.join(channel_folder[2], f"values.npy"), values[2])
    save_preview_image(values[0], values[1], values[2], os.path.join(clipboard_folder, f"{target_folder_name}.png"))


if __name__ == '__main__':
    parse_hydro("vibrationsdaten_Nov4-5_2022.parquet", "hydro")
