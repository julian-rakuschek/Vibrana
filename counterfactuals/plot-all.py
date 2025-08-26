import os.path
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler

chunk_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "chunks", "fault-detection", "fault-detection-A")

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


def plot_all_chunks():
    for file in os.listdir(chunk_folder):
        print(file)
        values = np.load(os.path.join(chunk_folder, file))
        plt.clf()
        fig, ax = plt.subplots(nrows=1, ncols=1)
        plot_tde_projection(values, 1000, ax)
        plt.savefig(f"plots/fingerprints/{file.removesuffix(".npy")}.png", dpi=300, transparent=True)


if __name__ == '__main__':
    plot_all_chunks()
