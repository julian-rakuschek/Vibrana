import random

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import ShortTimeFFT
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from parser.grav_waves import make_gravitational_waves


def vis_line_chart(data, title, hidden=None):
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(20, 7)
    ax.plot(data, color="black")
    ax.set_xlim(0, len(data))
    ax.set_axis_off()
    if hidden is not None:
        ax.plot(hidden, color="#ab47bc", linewidth=3.5)
    plt.savefig(title, bbox_inches='tight', dpi=300, transparent=True)


def plot_tde_projection(data, w, title, monochrome=False):
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(20, 20)
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)

    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    ax.scatter(projected[:, 0], projected[:, 1], s=20, c="#4A148C" if monochrome else plt.colormaps["turbo"](scores_norm))
    # ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")
    plt.savefig(title, bbox_inches='tight', dpi=300, transparent=True)


def color_line_chart(data, w, title):
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(20, 7)
    windows = sliding_window_view(data, window_shape=w)
    projected = PCA(n_components=2).fit_transform(windows)
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
    segments = []
    for i in range(len(data) - 1):
        segments.append([(i, data[i]), (i + 1, data[i + 1])])
    lc = LineCollection(segments, cmap="turbo", linewidth=3)
    lc.set_array(np.array(scores_norm))
    ax.add_collection(lc)
    # ax.plot(gw_signals[0], color="black", linewidth=3)
    ax.set_xlim(0, len(data))
    # ax.spines["top"].set_visible(False)
    # ax.spines["right"].set_visible(False)
    ax.set_axis_off()

    plt.savefig(title, bbox_inches='tight', dpi=200, transparent=True)


noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(1, snr=0.1, seed=42)
signal = noisy_signals_anomalous[0] * (10 ** 19)
signal = MinMaxScaler().fit_transform(signal.reshape(-1, 1)).reshape(1, -1)[0]
noise = noisy_signals_plain[0] * (10 ** 19)
noise = MinMaxScaler().fit_transform(noise.reshape(-1, 1)).reshape(1, -1)[0]
hidden = gw_signals[0] * (10 ** 19)
hidden = MinMaxScaler().fit_transform(hidden.reshape(-1, 1)).reshape(1, -1)[0]
w = 500

vis_line_chart(noise, "noise_line_chart_black.png")
vis_line_chart(noisy_signals_anomalous[0], "signal_line_chart_black.png", hidden=gw_signals[0])
plot_tde_projection(noise, w, "tde_noise_mono", monochrome=True)
plot_tde_projection(noise, w, "tde_noise_color", monochrome=False)
plot_tde_projection(signal, w, "tde_signal_mono", monochrome=True)
plot_tde_projection(signal, w, "tde_signal_color", monochrome=False)
color_line_chart(noise, w, "noise_line_chart_color.png")
color_line_chart(signal, w, "signal_line_chart_color.png")
