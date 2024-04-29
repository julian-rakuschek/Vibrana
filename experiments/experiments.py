import numpy as np
from scipy.signal import periodogram, ShortTimeFFT, savgol_filter
from scipy.signal.windows import gaussian

from Experiment import Experiment
from algorithms.defaultParameters import DWTCustomParameters
from algorithms.dwt_mlead import run_dwt
from util import signal_variance, butter_bandpass_filter


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


if __name__ == '__main__':
    dwt_experiment("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt")
    dwt_experiment("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde")
