import datetime
import json
import os
from bisect import bisect_right
from ctypes import POINTER, byref, c_double, c_int, c_int64, cast, create_string_buffer
from pathlib import Path

import numpy as np

from parser.lib.dewesoft import dwparser
from parser.lib.dewesoft.DWDataReaderHeader import DOUBLE_SIZE, DWMeasurementInfo, DWStatus, DWRaiseError
from vibrana.backend.data_loaders.dataLoaderBase import DataLoaderBase
from vibrana.backend.helper.config import get_config

conf = get_config()


class DewesoftLoader(DataLoaderBase):
    def __init__(self, dataset, subset, path=None):
        super().__init__()
        self.path = path or os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset)
        self.dataset = dataset
        self.subset = subset
        self.redis_prefix = f"vibrana:{dataset}:{subset}"

        self.files = sorted(Path(self.path).glob("*.dxd"))
        if not self.files:
            raise FileNotFoundError(f"No .dxd files found in {self.path}")

        self.file_infos = [self._read_file_info(str(file_path)) for file_path in self.files]
        self.file_offsets = []
        offset = 0
        for file_info in self.file_infos:
            self.file_offsets.append(offset)
            offset += file_info["sample_count"]
        self.data_size = offset
        self.fs = self.file_infos[0]["sample_rate"]

    def _read_file_info(self, file_path):
        with dwparser.dwt_reader(file_path) as reader:
            channels = dwparser.get_channel_list(reader)
            if not channels:
                raise ValueError(f"No Dewesoft channels found in {file_path}")

            channel = channels[0]
            measurement_info = DWMeasurementInfo(0, 0, 0, 0)
            if reader.DWGetMeasurementInfo(byref(measurement_info)) != DWStatus.DWSTAT_OK.value:
                DWRaiseError("DWDataReader: DWGetMeasurementInfo() failed")

            sample_count = dwparser.get_number_of_samples(reader, channel)
            return {
                "path": file_path,
                "sample_count": sample_count,
                "sample_rate": measurement_info.sample_rate,
            }

    def _read_file_slice(self, file_info, start_index, end_index):
        sample_count = end_index - start_index

        if sample_count <= 0:
            return np.array([])

        with dwparser.dwt_reader(file_info["path"]) as reader:
            channel = dwparser.get_channel_list(reader)[0]
            data = create_string_buffer(DOUBLE_SIZE * sample_count)
            time_stamp = create_string_buffer(DOUBLE_SIZE * sample_count)
            p_data = cast(data, POINTER(c_double))
            p_time_stamp = cast(time_stamp, POINTER(c_double))

            status = reader.DWGetScaledSamples(
                c_int(channel.index),
                c_int64(start_index),
                sample_count,
                p_data,
                p_time_stamp,
            )
            if status != DWStatus.DWSTAT_OK.value:
                DWRaiseError("DWDataReader: DWGetScaledSamples() failed")

            values = np.empty(sample_count)
            for i in range(sample_count):
                values[i] = p_data[i]

        return values

    def _read_file_timestamp(self, file_info, sample_index):
        with dwparser.dwt_reader(file_info["path"]) as reader:
            channel = dwparser.get_channel_list(reader)[0]
            data = create_string_buffer(DOUBLE_SIZE)
            time_stamp = create_string_buffer(DOUBLE_SIZE)
            p_data = cast(data, POINTER(c_double))
            p_time_stamp = cast(time_stamp, POINTER(c_double))

            status = reader.DWGetScaledSamples(
                c_int(channel.index),
                c_int64(sample_index),
                1,
                p_data,
                p_time_stamp,
            )
            if status != DWStatus.DWSTAT_OK.value:
                DWRaiseError("DWDataReader: DWGetScaledSamples() failed")

            return p_time_stamp[0]

    def get_slice(self, start_index=0, end_index=-1, as_numpy=False):
        start_index = int(start_index)
        end_index = int(end_index)
        start_index, end_index, _ = slice(start_index, end_index).indices(self.data_size)

        if start_index >= end_index:
            result = np.array([])
            return result if as_numpy else result.tolist()

        start_file = bisect_right(self.file_offsets, start_index) - 1
        end_file = bisect_right(self.file_offsets, end_index - 1) - 1

        chunks = []
        for file_index in range(start_file, end_file + 1):
            file_start = self.file_offsets[file_index]
            file_end = file_start + self.file_infos[file_index]["sample_count"]
            local_start = max(start_index, file_start) - file_start
            local_end = min(end_index, file_end) - file_start
            chunks.append(self._read_file_slice(self.file_infos[file_index], local_start, local_end))

        result = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
        if not as_numpy:
            return result.tolist()
        return result

    def get_first_last_timestamp(self):
        first_timestamp = self._read_file_timestamp(self.file_infos[0], 0)
        last_timestamp = self._read_file_timestamp(self.file_infos[-1], self.file_infos[-1]["sample_count"] - 1)
        return first_timestamp, last_timestamp


def generate_time_json(dataset, subset):
    loader = DewesoftLoader(dataset, subset)
    first_ts, last_ts = loader.get_first_last_timestamp()
    time_json = {
      "start_time": first_ts,
      "end_time": last_ts,
      "total_sample_points": loader.data_size,
      "display_as_delta": False
    }
    with open(os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "time.json"), "w") as f:
        json.dump(time_json, f, indent=4)

if __name__ == '__main__':
    dataset = "messfeld"
    subset = "FRE"
    loader = DewesoftLoader(dataset, subset)
    print(loader.get_slice(1000, 2000))
    generate_time_json(dataset, subset)
