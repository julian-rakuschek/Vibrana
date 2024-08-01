import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import periodogram, ShortTimeFFT, savgol_filter
from scipy.signal.windows import gaussian
from tslearn.preprocessing import TimeSeriesResampler
import stumpy
from numba import cuda
from matplotlib import cm
from Experiment import Experiment
from TakenMethod import TakenMethod
from algorithms.damp import DAMP
from algorithms.defaultParameters import DWTCustomParameters
from algorithms.dwt_mlead import run_dwt
from util import signal_variance, butter_bandpass_filter, reverse_windowing


def basic(folder):
    ex = Experiment(folder, name="basic", plot_fig_size=(40, 15))
    ex.plot_raw_signal()
    ex.ax.spines[['right', 'top']].set_visible(False)
    ex.ax.set_title("")
    ex.save()

def event_zoom(folder):
    ex = Experiment(
        folder, name="zoom", plot_mosaic=[["raw"], ["event"], ["event"]], plot_fig_size=(40, 15)
    )
    ex.plot_event_zoom(0)
    ex.save()

def variance_exp(folder, window_size=300):
    ex = Experiment(
        folder, name="variance", plot_rows=3, plot_fig_size=(50, 20)
    )
    var1 = signal_variance(ex.values, window_size=window_size)
    var2 = signal_variance(var1, window_size=window_size, smoothing_window=2000)

    ex.plot_raw_signal()
    ex.plot_time_series(var1, 1, "Variance", include_events=True, color="indigo")
    ex.plot_time_series(var2, 2, "Variance of Variance", include_events=True, color="purple")
    ex.save()

def periodogram_exp(folder):
    ex = Experiment(
        folder, name="periodogram", plot_mosaic=[["raw", "raw", "raw", "fft", "fft"]], plot_fig_size=(35, 10)
    )
    f, Pxx_spec = periodogram(ex.values, fs=ex.sample_rate, scaling="density")
    ex.ax["fft"].plot(f, Pxx_spec, color="navy")
    ex.ax["fft"].set_title("Periodogram")
    ex.ax["fft"].set_xlabel("Frequency")
    ex.ax["raw"].plot(ex.values, color="black")
    ex.ax["raw"].vlines(ex.event_indices, 0, np.max(ex.values), color="#ff4d4d", linewidth=1)
    ex.ax["raw"].scatter(ex.event_indices, np.tile(np.max(ex.values), len(ex.event_indices)), color="#ff4d4d", marker="v", s=60)
    ex.ax["raw"].set_title("Raw Signal")
    ex.ax["raw"].set_xlabel("Time")
    ex.save()

def butterworth_variance(folder):
    ex = Experiment(
        folder, name="butterworth", plot_rows=3, plot_fig_size=(35, 20)
    )
    filtered = butter_bandpass_filter(ex.values, 100, 650, ex.sample_rate)
    var = signal_variance(filtered, window_size=200, smoothing_window=2000)
    ex.plot_raw_signal()
    ex.plot_time_series(filtered, 1, "Signal with applied bandpass filter on low frequency spectrum")
    ex.plot_time_series(var, 2, "Variance of filtered signal")
    ex.save()


def spectrogram(folder):
    ex = Experiment(
        folder, name="spectrogram", plot_mosaic=[["raw"], ["event"], ["event"], ["event"]], plot_fig_size=(30, 15)
    )

    w = gaussian(50, std=24, sym=True)  # symmetric Gaussian window
    SFT = ShortTimeFFT(w, hop=10, fs=ex.sample_rate, mfft=10_000, scale_to='psd')
    Sx = SFT.spectrogram(ex.values)  # perform the STFT
    Sx_dB = 10 * np.log10(np.fmax(Sx, 0.00005))

    ex.plot_raw_signal()
    ex.ax["raw"].set_xlim(0, len(ex.values))
    ex.ax["event"].imshow(Sx_dB, origin='lower', aspect='auto', extent=SFT.extent(len(ex.values)), cmap='turbo')
    for ei in ex.event_indices:
        ex.ax["event"].axvline(ei / ex.sample_rate, color="#ff4d4d", linewidth=1)
    ex.ax["event"].set_title("Spectrogram", fontsize=20)
    ex.save()

def dwt_experiment(folder):
    ex = Experiment(
        folder, name="dwt", plot_rows=3, plot_fig_size=(30, 20)
    )
    res = run_dwt(DWTCustomParameters(quantile_epsilon=0.01), ex.values)
    smoothed = savgol_filter(res, 3000, polyorder=3)

    ex.plot_raw_signal()
    ex.plot_time_series(res, 1, "DWT Anomaly Scores")
    ex.plot_time_series(smoothed, 2, "Smoothed Anomaly Scores")
    ex.save()


def taken_cloud_events(folder):
    ex = TakenMethod(
        folder, name="point_cloud_events", plot_fig_size=(30, 30)
    )
    ex.points_to_cloud()
    scores = ex.score_by_events()
    ex.plot_point_cloud(scores)
    ex.save()

def taken_cloud_radius(folder):
    ex = TakenMethod(
        folder, name="point_cloud_radius", plot_fig_size=(30, 30)
    )
    proj = ex.points_to_cloud()
    scores = ex.score_by_radius(proj, True)
    ex.plot_point_cloud(scores)
    ex.save()

def taken_anomaly_scores(folder):
    ex = TakenMethod(
        folder, name="taken_method", plot_rows=2, plot_fig_size=(35, 20)
    )
    proj = ex.points_to_cloud()
    scores = ex.score_by_radius(proj, True)
    scores = reverse_windowing(scores, ex.window_size)
    anomaly_scores = np.abs(np.diff(scores, n=2)[20:-20])[:-300]
    anomaly_scores = TimeSeriesResampler(sz=len(scores)).fit_transform(anomaly_scores.reshape(1, -1))[0, :, 0]

    ex.plot_colored_signal(scores, title="Raw Signal Colored by Radius in Taken Point Cloud")
    ex.plot_time_series(anomaly_scores, 1, title="Change of The Radius")
    ex.save()


def matrix_profile_experiment(folder):
    ex = Experiment(
        folder, name="matrix_profile", plot_rows=3, plot_fig_size=(35, 20)
    )
    all_gpu_devices = [device.id for device in cuda.list_devices()]
    mat = np.load("matrix.npy", allow_pickle=True)[:, 0]
    mat2 = np.log(signal_variance(mat))
    ex.plot_raw_signal()
    ex.plot_time_series(mat, 1, "Matrix Profile", True)
    ex.plot_time_series(mat2, 2, "Matrix Profile", True)



    # matrix_profile = stumpy.gpu_stump(ex.values, m=7000, device_id=all_gpu_devices)
    # with Client() as dask_client:
    #     matrix_profile = stumpy.stumped(dask_client, ex.values, m=7000)
    # np.save("matrix.npy", matrix_profile)
    # print(matrix_profile)
    ex.save()


def incremental_PCA_experiment(folder):
    ex = TakenMethod(
        folder, name="inc_pca", plot_rows=3, plot_fig_size=(30, 30), window_size=1_000
    )
    proj = ex.points_to_cloud(incremental=True)
    scores = ex.score_by_radius(proj, True)
    ex.plot_point_cloud(scores)
    ex.save()


def damp_experiment(folder):
    ex = Experiment(
        folder, name="damp", plot_rows=2, plot_fig_size=(35, 20)
    )
    res = DAMP(ex.values, 40, 1, 3000, 0, False)
    print(res)


def reduce_exp_1(folder):
    ex = Experiment(
        folder, name="reduced_100000", plot_rows=1, plot_fig_size=(35, 20)
    )
    ex.reduce(100000)
    ex.plot_raw_signal()
    ex.save()


def reduce_exp_2(folder):
    ex = TakenMethod(
        folder, name="reduced_cloud_100000", plot_rows=1, plot_fig_size=(35, 35)
    )
    ex.reduce(100000, 700)
    proj = ex.points_to_cloud(incremental=False)
    scores = ex.score_by_radius(proj, True)
    ex.plot_point_cloud(scores, s=50)
    ex.save()


def cloud_with_trace(folder):
    ex = TakenMethod(
        folder, name="point_cloud_radius_trace", plot_fig_size=(30, 30), window_size=2_000
    )
    # ex.reduce(1000, 7)
    start_i = ex.event_indices[1] - (ex.window_size // 2)
    end_i = ex.event_indices[1] + (ex.window_size // 2)
    proj = ex.points_to_cloud(False)
    ex.plot_point_cloud_trace(start_i, end_i)
    ex.save()


if __name__ == '__main__':
    # reduce_exp_1("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt")
    # cloud_with_trace("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt")
    # matrix_profile_experiment("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde")
    # taken_anomaly_scores("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde")
    cloud_with_trace("16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde gemischt 31,5-62")
