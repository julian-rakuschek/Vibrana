import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA, KernelPCA
from sklearn.manifold import TSNE, Isomap
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from umap import UMAP


def plot_tde_projection(data, w, ax, monochrome=False, method="PCA"):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    if method == "PCA":
        projected = PCA(n_components=2).fit_transform(windows)
    elif method == "UMAP":
        projected = UMAP(n_components=2).fit_transform(windows)
    elif method == "TSNE":
        projected = TSNE(n_components=2).fit_transform(windows)
    elif method == "ISOMAP":
        projected = Isomap(n_components=2).fit_transform(windows)
    elif method == "KernelPCA Poly":
        projected = KernelPCA(n_components=2, kernel="poly").fit_transform(windows)
    elif method == "KernelPCA Rbf":
        projected = KernelPCA(n_components=2, kernel="rbf").fit_transform(windows)
    else:
        raise ValueError("Unknown Method")

    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    ax.scatter(projected[:, 0], projected[:, 1], s=8, c="black" if monochrome else plt.colormaps["turbo"](scores_norm))
    ax.set_title(method, fontsize=30)
    ax.axis("off")


values = np.load("values.npy")[:10_000]
fig, ax = plt.subplots(ncols=3, nrows=2, figsize=(30, 20))
plot_tde_projection(values, 1000, ax[0, 0], method="PCA")
plot_tde_projection(values, 1000, ax[0, 1], method="KernelPCA Poly")
plot_tde_projection(values, 1000, ax[0, 2], method="KernelPCA Rbf")
plot_tde_projection(values, 1000, ax[1, 0], method="UMAP")
plot_tde_projection(values, 1000, ax[1, 1], method="TSNE")
plot_tde_projection(values, 1000, ax[1, 2], method="ISOMAP")


plt.savefig("tsne.png", bbox_inches='tight', dpi=50)
