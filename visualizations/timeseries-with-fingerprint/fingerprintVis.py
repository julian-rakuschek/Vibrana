import math
import os

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler


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
    ax.scatter(projected[:, 0], projected[:, 1], s=8, c="black" if monochrome else plt.colormaps["turbo"](scores_norm))
    # ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")

def plot_ts(data, ax):
    ax.plot(data, c="black")

def main(file_path):
    ts = np.load(file_path)
    fig, ax = plt.subplot_mosaic([["ts", "ts", "ts", "tde"]])
    fig.set_size_inches(20, 5)

    plot_ts(ts, ax["ts"])
    plot_tde_projection(ts, 500, ax["tde"])
    plt.savefig(f"undamaged.png", bbox_inches='tight', dpi=200)

if __name__ == '__main__':
    main("/home/vulturemox/Coding/PhD/PRESENT/Vibrana/data/prepared-signals/chunks/fault-detection/fault-detection-A/values-undamaged-0000.npy")