import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from tqdm import tqdm
from tslearn.preprocessing import TimeSeriesResampler


def generate_time_series():
    sampling_rate = 100  # Number of samples per second
    duration = 20  # Duration of the signal in seconds
    start_frequency = 0.2  # Starting frequency in Hz
    end_frequency = 1  # Ending frequency in Hz
    t = np.linspace(0, duration, sampling_rate * duration)
    frequencies = np.linspace(start_frequency, end_frequency, len(t))
    sine_wave = np.sin(2 * np.pi * frequencies * t)
    return sine_wave

def generate_time_series_2():
    sampling_rate = 100  # Number of samples per second
    duration = 20  # Duration of the signal in seconds
    frequency_1 = 0.2  # Starting frequency in Hz
    frequency_2 = 1  # Ending frequency in Hz
    t = np.linspace(0, duration, sampling_rate * duration)
    sine_wave_1 = np.sin(2 * np.pi * frequency_1 * t)
    sine_wave_2 = np.sin(2 * np.pi * frequency_2 * t)
    return np.concatenate([sine_wave_1, sine_wave_2])

def multiPlot(sine_wave, w):
    plot_mosaic = [
        ["wave", "wave", "wave", "TDE", "TDE"],
        ["wave", "wave", "wave", "TDE", "TDE"],
        ["freq", "freq", "freq", "TDE", "TDE"]
    ]
    plt.clf()
    fig, ax = plt.subplot_mosaic(plot_mosaic)
    plt.subplots_adjust(wspace=0.1, hspace=0.3)
    fig.set_size_inches(20, 10)


    windows = sliding_window_view(sine_wave, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)
    projected[:, 0] = (np.array(projected[:, 0]) - np.min(projected[:, 0])) / (np.max(projected[:, 0]) - np.min(projected[:, 0]))
    projected[:, 0] -= 0.5
    projected[:, 1] = (np.array(projected[:, 1]) - np.min(projected[:, 1])) / (np.max(projected[:, 1]) - np.min(projected[:, 1]))
    projected[:, 1] -= 0.5
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = (np.array(scores) - np.min(scores)) / (np.max(scores) - np.min(scores))
    scores_norm_resampled = TimeSeriesResampler(sz=len(sine_wave)).fit_transform(scores_norm).flatten()
    ax["wave"].set_xlim(0, len(sine_wave))
    ax["wave"].set_title("Sine Wave with increasing frequency over time", fontsize=30)

    segments = []
    for i in range(len(sine_wave) - 1):
        segments.append([(i, sine_wave[i]), (i + 1, sine_wave[i + 1])])
    lc = LineCollection(segments, cmap="turbo", linewidth=3)
    lc.set_array(np.array(scores_norm_resampled))
    # ax["wave"].add_collection(lc)
    ax["wave"].plot(sine_wave, color="black")
    ax["wave"].set_xlim(0, len(sine_wave))

    ax["freq"].imshow(scores_norm_resampled.reshape(1, -1), cmap="turbo", aspect='auto', interpolation='nearest')
    # ax["freq"].set_xlim(0, len(scores_norm_resampled))
    ax["freq"].set_title("Frequency over time", fontsize=30)

    ax["TDE"].scatter(projected[:, 0], projected[:, 1], s=8, c=plt.colormaps["turbo"](scores_norm))
    # ax["TDE"].get_xaxis().set_visible(False)
    ax["TDE"].set_title(f"TDE w={w}", fontsize=30)

    plt.savefig(f"sine/vibration-tde.png", bbox_inches='tight', dpi=300)
    plt.close(fig)


def slice_and_project(sine_wave, w, n_segments):
    window_size = len(sine_wave) // n_segments
    plot_mosaic = [
        ["line" for _ in range(n_segments)],
        [f"projection{i}" for i in range(n_segments)]
    ]
    fig, ax = plt.subplot_mosaic(plot_mosaic)
    fig.set_size_inches(10 * n_segments, 20)

    cuts = []
    arrow_locations = []
    for i in tqdm(range(n_segments)):
        if i != 0:
            cuts.append(i * window_size)
            arrow_locations.append((i * window_size + (i + 1) * window_size) // 2)
        subset = sine_wave[i * window_size:(i + 1) * window_size]
        windows = sliding_window_view(subset, window_shape=w)
        projected = PCA(n_components=2).fit_transform(windows)

        scores = []
        for point in projected:
            scores.append(np.linalg.norm(point))
        scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

        ax[f"projection{i}"].set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
        ax[f"projection{i}"].set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
        ax[f"projection{i}"].scatter(projected[:, 0], projected[:, 1], s=8, c=plt.colormaps["turbo"](scores_norm))
        ax[f"projection{i}"].axis("off")

    ax["line"].set_xlim(0, len(sine_wave))
    ax["line"].plot(sine_wave, color="black", linewidth=5)
    ax["line"].tick_params(axis='both', labelsize=50)
    ax["line"].vlines(cuts, ymin=np.min(sine_wave), ymax=np.max(sine_wave), color="#ff6361", linewidth=3)
    plt.savefig(f"slices.png", bbox_inches='tight')

sine_wave = generate_time_series_2()
slice_and_project(sine_wave, 2, 6)
