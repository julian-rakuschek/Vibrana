# Author: Julian Rakuschek
# julian.rakuschek@tugraz.at

import contextlib
import math
import os
import shutil
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from DWDataReaderHeader import *
from ctypes import *
import _ctypes

# from https://dewesoft.com/download/developer-downloads
# "Dewesoft Data Reader Library" -> DWDataReaderExample.py

def init_reader_lib():
    if os.name == 'nt':
        reader_lib = cdll.LoadLibrary(f'{Path(__file__).parents[0]}/DWDataReaderLib64.dll')
    else:
        reader_lib = cdll.LoadLibrary(f'{Path(__file__).parents[0]}/DWDataReaderLib64.so')
    if reader_lib.DWInit() != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWInit() failed")
    print("DWDataReader version: " + str(reader_lib.DWGetVersion()))
    if reader_lib.DWAddReader() != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWAddReader() failed")
    return reader_lib

@contextlib.contextmanager
def dwt_reader(folder):
    reader = init_reader_lib()
    try:
        file_path = os.path.join(Path(__file__).parents[1], "data", folder, f"{folder}.dxd")
        file_name = c_char_p(file_path.encode())
        file_info = DWFileInfo(0, 0, 0)
        if reader.DWOpenDataFile(file_name, c_void_p(addressof(file_info))) != DWStatus.DWSTAT_OK.value:
            DWRaiseError("DWDataReader: DWOpenDataFile() failed")
        yield reader
    except Exception as e:
        print(e)
    finally:
        if reader.DWCloseDataFile() != DWStatus.DWSTAT_OK.value:
            DWRaiseError("DWDataReader: DWCloseDataFile() failed")
        if reader.DWDeInit() != DWStatus.DWSTAT_OK.value:
            DWRaiseError("DWDataReader: DWDeInit() failed")


def print_measurement_info(reader):
    measurement_info = DWMeasurementInfo(0, 0, 0, 0)
    if reader.DWGetMeasurementInfo(c_void_p(addressof(measurement_info))) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetMeasurementInfo() failed")

    print("Sample rate: %.2f" % measurement_info.sample_rate)
    print("Start measure time: %.2f" % measurement_info.start_measure_time)
    print("Start store time: %.2f" % measurement_info.start_store_time)
    print("Duration: %.2f" % measurement_info.duration)

def export_metadata(reader, filename: str):
    file_name = c_char_p(filename.encode())
    if reader.DWExportHeader(file_name) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWExportHeader() failed")

def get_total_channels(reader):
    num = reader.DWGetChannelListCount()
    if num == -1:
        DWRaiseError("DWDataReader: DWGetChannelListCount() failed")
    return num

def get_channel_list(reader):
    num_channels = get_total_channels(reader)
    ch_list = (DWChannel * num_channels)()
    if reader.DWGetChannelList(byref(ch_list)) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetChannelList() failed")
    return ch_list

def print_channel_properties(channel):
    print("Index: %d" % channel.index)
    print("Name: %s" % channel.name.decode())
    print("Unit: %s" % channel.unit.decode())
    print("Description: %s" % channel.description.decode())

def get_channel_factors(reader, channel):
    idx = c_int(channel.index)
    ch_scale = c_double()
    ch_offset = c_double()
    if reader.DWGetChannelFactors(idx, byref(ch_scale), byref(ch_offset)) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetChannelFactors() failed")
    return ch_scale.value, ch_offset.value

def get_number_of_samples(reader, channel):
    idx = c_int(channel.index)
    sample_cnt = reader.DWGetScaledSamplesCount(idx)
    if sample_cnt < 0:
        DWRaiseError("DWDataReader: DWGetScaledSamplesCount() failed")
    return sample_cnt

def get_data(reader, channel):
    idx = c_int(channel.index)
    sample_cnt = get_number_of_samples(reader, channel)
    data = create_string_buffer(DOUBLE_SIZE * sample_cnt * channel.array_size)
    time_stamp = create_string_buffer(DOUBLE_SIZE * sample_cnt)
    p_data = cast(data, POINTER(c_double))
    p_time_stamp = cast(time_stamp, POINTER(c_double))

    if reader.DWGetScaledSamples(idx, c_int64(0), sample_cnt, p_data, p_time_stamp) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetScaledSamples() failed")

    values, timestamps = [], []
    for j in range(0, sample_cnt):
        for k in range(0, channel.array_size):
            values.append(p_data[j * channel.array_size + k])
            timestamps.append(p_time_stamp[j])
    values = np.array(values)
    timestamps = np.array(timestamps)
    return values, timestamps

def get_events(reader):
    event_list_cnt = reader.DWGetEventListCount()
    EventArrayType = DWEvent * event_list_cnt
    event_list = EventArrayType()
    if reader.DWGetEventList(byref(event_list)) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetEventList() failed")
    return [e.time_stamp for e in event_list if e.event_type == 20]

def process_folder(folder):
    def find_nearest(array, value):
        idx = np.searchsorted(array, value, side="left")
        if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
            return idx - 1
        else:
            return idx

    print(f"Processing {folder}")
    with dwt_reader(folder) as reader:
        channels = get_channel_list(reader)
        values, timestamps = get_data(reader, channels[0])
        events = get_events(reader)
    event_indices = [find_nearest(timestamps, e) for e in events]

    plt.clf()
    plt.figure(figsize=(100, 10))
    plt.plot(values, color="black")
    plt.vlines(event_indices, np.min(values), np.max(values), color="r")

    base_path = f'{Path(__file__).parents[1]}/data/{folder}'
    plt.savefig(f"{base_path}/plot_with_events.png", bbox_inches='tight')
    np.save(f"{base_path}/values.npy", values)
    np.save(f"{base_path}/timestamps.npy", timestamps)
    np.save(f"{base_path}/event_timestamps.npy", np.array(events))

def process_data_folder():
    base_path = f'{Path(__file__).parents[1]}/data/'
    for file in os.listdir(base_path):
        if file.endswith('dxd'):
            folder_name = file.replace(".dxd", "")
            if os.path.exists(os.path.join(base_path, folder_name)):
                shutil.rmtree(os.path.join(base_path, folder_name))
            os.makedirs(os.path.join(base_path, folder_name))
            shutil.move(os.path.join(base_path, file), os.path.join(base_path, folder_name, file))
            process_folder(folder_name)


if __name__ == '__main__':
    process_data_folder()
