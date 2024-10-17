import json
import math
import os
import time
from pathlib import Path

import numpy as np
import redis
from redis import Redis

from parser.dwparser import process_file
from parser.extract_snippets import split_and_process_time_series

raw_folder = os.path.join(Path(__file__).parents[3], "data", "raw")
parsed_folder = os.path.join(Path(__file__).parents[3], "data", "parsed")
split_folder = os.path.join(Path(__file__).parents[3], "data", "split")


def parse_file(machine: str, filename: str, prefix: str, max_sample_size: int, save_parsed: bool, cutoff_ratio: float, projection_window_size: int, redis_client: Redis):
    print(f"Parsing {filename}")
    r_key = f"vibrana:{machine}:{filename}"
    if redis_client:
        status = {
            "dwparse": {"status": "processing"},
            "split": {"status": "waiting for Dewesoft parsing to complete", "items": {}}
        }
        redis_client.set(r_key, json.dumps(status))

    values, timestamps, events = process_file(os.path.join(raw_folder, filename))

    if cutoff_ratio is not None and 0 < cutoff_ratio < 0.5:
        cut_index = math.floor(len(values)*cutoff_ratio)
        values = values[cut_index:len(values) - cut_index]
        timestamps = timestamps[cut_index:len(values) - cut_index]

    if save_parsed:
        file_parsed_folder = os.path.join(parsed_folder, filename.replace(".dxd", ""))
        Path(file_parsed_folder).mkdir(parents=True, exist_ok=True)
        np.save(os.path.join(file_parsed_folder, "values.npy"), values)
        np.save(os.path.join(file_parsed_folder, "timestamps.npy"), timestamps)
        np.save(os.path.join(file_parsed_folder, "event_timestamps.npy"), np.array(events))

    if redis_client:
        status["dwparse"]["status"] = "done"
        redis_client.set(r_key, json.dumps(status))

    split_and_process_time_series(values, timestamps, events, filename, prefix, machine, max_sample_size, projection_window_size, redis_client)
