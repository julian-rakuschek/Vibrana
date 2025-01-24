import os
from math import floor
from pathlib import Path

import numpy as np

from parser.dwparser import process_file
from parser.extract_chunks import split_and_process_time_series

data_folder = os.path.join(Path(__file__).parents[1], "data", "raw", "binder")
parsed_folder = os.path.join(Path(__file__).parents[1], "data", "parsed", "binder")
chunk_folder = os.path.join(Path(__file__).parents[1], "data", "chunks")


def parse_folder(
        folder: str, window_size: int = 2000,
        max_sample_size: int = 100_000,
        prefix: str = "signal", prefix_ground_truth: bool = False,
        cutoff_ratio: float = 0.2
):
    """
    Parse dxd files that contain vibrations and put all relevant information in npy arrays

    Args:
        folder: Name of a subset from the binder dataset
        window_size: For the time delay embedding
        max_sample_size: How many data points should be contained in one chunk
        prefix: The prefix in the name of each chunk
        prefix_ground_truth: If activated, chunks will have "anomalous" in their name of the signal contains an anomaly
        cutoff_ratio: How much to cut from the beginning and ending of the signal, this is important since the experiment always has some start-up phase in the beginning, same when the experiment ends
    """
    folder_path = os.path.join(data_folder, folder)
    if not os.path.exists(folder_path):
        raise Exception(f"{folder_path} does not exist")
    print(f"==== {folder} ====")

    for file in os.listdir(folder_path):
        print(file)
        if not file.endswith("dxd"):
            continue
        # process_file calls the dxd parser to process the file
        values, timestamps, events = process_file(os.path.join(folder_path, file))
        if cutoff_ratio is not None and 0 < cutoff_ratio < 0.5:
            cut_index = floor(len(values) * cutoff_ratio)
            values = values[cut_index:len(values) - cut_index]
            timestamps = timestamps[cut_index:len(values) - cut_index]

        file_parsed_folder = os.path.join(parsed_folder, folder, file.replace(".dxd", ""))
        Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)
        np.save(os.path.join(file_parsed_folder, "values.npy"), values)
        np.save(os.path.join(file_parsed_folder, "timestamps.npy"), timestamps)
        np.save(os.path.join(file_parsed_folder, "event_timestamps.npy"), np.array(events))

        if prefix_ground_truth:
            prefix = "anomalous" if "gemischt" in file.lower() else "normal"
        split_and_process_time_series(values, timestamps, events, file, prefix, "binder", folder, max_sample_size, window_size, None, limit=7)


if __name__ == '__main__':
    parse_folder("1")
