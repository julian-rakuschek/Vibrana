import matplotlib.pyplot as plt
import numpy as np
import emd
from numpy.lib._stride_tricks_impl import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from parser.grav_waves import make_gravitational_waves


def plot_time_series(ax, data: np.ndarray, title: str, color: str = "indigo"):
    ax.plot(data, color=color)
    ax.set_title(title, fontsize=20)
    ax.set_xlim(0, len(data))

def plot_tde_projection(data, w, ax, monochrome=False):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)

    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    ax.scatter(projected[:, 0], projected[:, 1], s=5, c="black" if monochrome else plt.colormaps["turbo"](scores_norm))
    # ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")

def plot_emd_result(x, imf, title, w=2000, hidden_signal=None):
    plot_mosaic = [
        ["x", "x", "x", "projected_x"]
    ]
    for i in range(imf.shape[1]):
        plot_mosaic.append([str(i), str(i), str(i), f"projected_{i}"])

    plt.clf()
    fig, ax = plt.subplot_mosaic(plot_mosaic)
    fig.set_size_inches((len(plot_mosaic[0]) * 5, len(plot_mosaic) * 5))
    fig.suptitle(title, fontsize=25)
    plt.subplots_adjust(top=0.96, bottom=0, hspace=0.5)
    plot_time_series(ax["x"], x, "Original", "black")
    plot_tde_projection(x, w, ax["projected_x"])
    if hidden_signal is not None:
        ax["x"].plot(hidden_signal, color="#ab47bc", linewidth=3.5)

    cmap = plt.get_cmap('turbo')
    for i in range(imf.shape[1]):
        plot_time_series(ax[str(i)], imf[:, i], f"IMF {i}", cmap(i / (imf.shape[1] + 1)))
        plot_tde_projection(imf[:, i], 2000, ax[f"projected_{i}"])
    filename = title.lower().replace(" ", "-")
    plt.savefig(f"{filename}.png", bbox_inches='tight', dpi=100)

def hydro_emd_experiment():
    x = np.load("data/hydro-2.npy")
    imf = emd.sift.sift(x)
    plot_emd_result(x, imf, "Hydro Power Plant State 2")

def grav_waves_emd():
    noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(1, snr=0.1, seed=42)
    signal = noisy_signals_anomalous[0] * (10 ** 19)
    signal = MinMaxScaler().fit_transform(signal.reshape(-1, 1)).reshape(1, -1)[0]
    noise = noisy_signals_plain[0] * (10 ** 19)
    noise = MinMaxScaler().fit_transform(noise.reshape(-1, 1)).reshape(1, -1)[0]
    hidden = gw_signals[0] * (10 ** 19)
    hidden = MinMaxScaler().fit_transform(hidden.reshape(-1, 1)).reshape(1, -1)[0]
    w = 1000

    imf = emd.sift.ensemble_sift(signal)
    plot_emd_result(signal, imf, "Gaussian Noise with Hidden Signal", w, hidden)

    imf = emd.sift.ensemble_sift(noise)
    plot_emd_result(noise, imf, "Gaussian Noise", w)

def sine_wave_with_noise():
    num_points = 10000
    sampling_rate = 1000
    duration = num_points / sampling_rate
    frequency = 2
    t = np.linspace(0, duration, num_points, endpoint=False)
    sine_wave = np.sin(2 * np.pi * frequency * t)
    with_noise = 5 * np.random.randn(num_points)
    sine_wave_noise = sine_wave + with_noise

    imf = emd.sift.complete_ensemble_sift(sine_wave_noise)
    plot_emd_result(sine_wave_noise, imf, "Sine Wave with Noise", 1000, sine_wave)

def motor_bearing_emd_experiment():
    x = np.load("data/motor-bearing.npy")
    imf = emd.sift.sift(x)
    plot_emd_result(x, imf, "Motor Bearing")


def motor_run_to_failure_emd_experiment():
    x = np.load("data/motor-run-to-failure-start.npy")
    imf = emd.sift.sift(x)
    plot_emd_result(x, imf, "Motor Run To Failure - Start - Good State")

    x = np.load("data/motor-run-to-failure-end.npy")
    imf = emd.sift.sift(x)
    plot_emd_result(x, imf, "Motor Run To Failure - End - Bad State")


motor_run_to_failure_emd_experiment()