import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import butter, lfilter, savgol_filter
from tslearn.preprocessing import TimeSeriesResampler


def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
        return idx - 1
    else:
        return idx

def derive_sample_rate(timestamps):
    time_intervals = np.diff(timestamps)
    average_interval = np.mean(time_intervals)
    sample_rate = 1 / average_interval
    return sample_rate

def signal_variance(signal, window_size=300, smoothing_window=None):
    variance_scores = sliding_window_view(signal, window_shape=window_size)
    variance_scores = np.var(variance_scores, axis=1)
    variance_scores = TimeSeriesResampler(sz=len(variance_scores)).fit_transform(variance_scores.reshape(1, -1))[0, :, 0]
    if smoothing_window is not None and smoothing_window > 0:
        variance_scores = savgol_filter(variance_scores, smoothing_window, 3)
    return variance_scores

def butter_bandpass(lowcut, highcut, fs, order=5) -> (np.ndarray, np.ndarray):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y
