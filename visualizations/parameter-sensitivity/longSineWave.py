import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from tslearn.preprocessing import TimeSeriesResampler


def generate_time_series():
    sampling_rate = 1000  # Number of samples per second
    duration = 20  # Duration of the signal in seconds
    start_frequency = 0.5  # Starting frequency in Hz
    end_frequency = 20  # Ending frequency in Hz
    t = np.linspace(0, duration, sampling_rate * duration)
    frequencies = np.linspace(start_frequency, end_frequency, len(t))
    sine_wave = np.sin(2 * np.pi * frequencies * t)
    return frequencies, sine_wave


def multiPlot(frequencies, sine_wave, w):
    plot_mosaic = [
        ["wave", "wave", "wave", "TDE"],
        ["freq", "freq", "freq", "TDE"]
    ]
    plt.clf()
    fig, ax = plt.subplot_mosaic(plot_mosaic)
    plt.subplots_adjust(wspace=0.1, hspace=0.3)
    fig.set_size_inches(20, 10)


    windows = sliding_window_view(sine_wave, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
    scores_norm_resampled = TimeSeriesResampler(sz=len(sine_wave)).fit_transform(scores_norm).flatten()
    print(len(sine_wave))
    print(len(scores_norm_resampled))
    ax["wave"].set_xlim(0, len(sine_wave))
    ax["wave"].set_title("Sine Wave with increasing frequency over time", fontsize=30)

    segments = []
    for i in range(len(sine_wave) - 1):
        segments.append([(i, sine_wave[i]), (i + 1, sine_wave[i + 1])])
    lc = LineCollection(segments, cmap="turbo", linewidth=3)
    lc.set_array(np.array(scores_norm_resampled))
    ax["wave"].add_collection(lc)

    ax["freq"].plot(frequencies, color="black")
    ax["freq"].set_xlim(0, len(frequencies))
    ax["freq"].set_title("Frequency over time", fontsize=30)

    ax["TDE"].scatter(projected[:, 0], projected[:, 1], s=8, c=plt.colormaps["turbo"](scores_norm))
    ax["TDE"].get_xaxis().set_visible(False)
    ax["TDE"].set_title(f"TDE w={w}", fontsize=30)

    plt.savefig(f"sine/vibration-tde-{str(w).zfill(4)}.png", bbox_inches='tight', dpi=300)
    plt.close(fig)

frequencies, sine_wave = generate_time_series()
multiPlot(frequencies, sine_wave, 10)
