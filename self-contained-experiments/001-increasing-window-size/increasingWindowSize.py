import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
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


def plot_tdes():
    window_steps = [40, 80, 160, 320, 640, 1280, 2560]

    arr = np.load("motor-run-to-failure.npy")

    for w in window_steps:
        plt.clf()
        fig, ax = plt.subplots()
        fig.set_size_inches(10, 10)
        plot_tde_projection(arr, w, ax)
        plt.savefig(f"TDE_{w}.png", dpi=300, transparent=True)


if __name__ == '__main__':
    plot_tdes()
