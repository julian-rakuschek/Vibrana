import math
import os

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def compute_projection(data, w):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projector = PCA(n_components=2)
    projector.fit(windows)
    return projector.transform(windows), np.sum(projector.explained_variance_ratio_)

def plot_fingerprints(projected_list, explained_variance_ratios, min, max, title):
    explained_variance_ratios_normalized = (np.array(explained_variance_ratios) - min) / (max - min)

    plt.clf()
    cols = 5
    rows = math.ceil(len(projected_list) / cols)
    fig, ax = plt.subplots(nrows=rows, ncols=cols)
    fig.set_size_inches((cols * 6, rows * 5))

    col_idx = 0
    row_idx = 0
    for projected, ex, ex_norm in zip(projected_list, explained_variance_ratios, explained_variance_ratios_normalized):
        ax[row_idx, col_idx].scatter(projected[:, 0], projected[:, 1],
                                     s=1, color=plt.colormaps["viridis"](ex_norm))
        ax[row_idx, col_idx].set_title(f"{ex:.4f}")
        col_idx += 1
        if col_idx == cols:
            col_idx = 0
            row_idx += 1

    # Create a scalar mappable for the colorbar
    norm = plt.Normalize(vmin=min, vmax=max)
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
    sm.set_array([])

    # Add the colorbar
    cbar = fig.colorbar(sm, ax=ax.ravel().tolist(), shrink=0.5)
    cbar.set_label("Explained Variance Ratio", fontsize=25)
    cbar.ax.tick_params(labelsize=20)

    filename = title.lower().replace(" ", "-")
    fig.suptitle(title, fontsize=30)
    plt.savefig(f"{filename}.png", bbox_inches='tight')



tdes_damaged, tdes_undamaged = [], []
ex_damaged, ex_undamaged = [], []

for file in os.listdir("./vis-data"):
    print(file)
    data = np.load(f"./vis-data/{file}")
    projected, ex = compute_projection(data, 1000)
    if "undamaged" in file:
        tdes_undamaged.append(projected)
        ex_undamaged.append(ex)
    else:
        tdes_damaged.append(projected)
        ex_damaged.append(ex)
min_ex = np.min([*ex_damaged, *ex_undamaged])
max_ex = np.max([*ex_damaged, *ex_undamaged])

plot_fingerprints(tdes_damaged, ex_damaged, min_ex, max_ex, "Explained Variance Ratios for Damaged Bearings")
plot_fingerprints(tdes_undamaged, ex_undamaged, min_ex, max_ex, "Explained Variance Ratios for Undamaged Bearings")
# print(ex_damaged)
# print(ex_undamaged)

