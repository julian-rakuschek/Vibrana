import numpy as np
from matplotlib import pyplot as plt
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
    ax.scatter(projected[:, 0], projected[:, 1], s=20, c="#4A148C" if monochrome else plt.colormaps["turbo"](scores_norm))
    # ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")


vibrations = np.load("motor-run-to-failure.npy")
window_steps = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

for w in window_steps:
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(20, 20)
    print(f"Window Size {w}")
    plot_tde_projection(vibrations, w, ax, monochrome=True)
    plt.savefig(f"plots/tde-{str(w).zfill(4)}.png", dpi=300, bbox_inches='tight', transparent=True)
    plt.close(fig)
