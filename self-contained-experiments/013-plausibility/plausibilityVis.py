import copy
import os
import pickle
from typing import List, Self

import emd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numba
import numpy as np
from matplotlib.colors import ListedColormap
from numpy.lib._stride_tricks_impl import sliding_window_view
from openTSNE import TSNE
from scipy.spatial import ConvexHull
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from umap import UMAP

from parser.lib.dewesoft.dwparser import export_metadata

label_color_map = {
    "damaged": "#e91e63",
    "undamaged": "#43a047",
}

label_description_map = {
    "damaged": "Damaged",
    "undamaged": "Undamaged",
}


# ------------------------------------------------------------------------

class Chunk:
    def __init__(self, data, label, w):
        self.data = data
        self.label = label
        self.w = w
        self.windows = sliding_window_view(data, window_shape=w)
        self.projected = PCA(n_components=2).fit_transform(self.windows)
        self.emd = emd.sift.sift(data).T

    def get_radii(self, projected=False):
        return np.linalg.norm(self.projected if projected else self.windows, axis=1)

    def get_max_radius(self, projected=False):
        return np.max(self.get_radii(projected))

    def get_histogram(self, projected=False, max_radius=None):
        radii = self.get_radii(projected)
        if max_radius is None:
            max_radius = self.get_max_radius(projected)
        counts, bins = np.histogram(radii, bins=20, range=(0, max_radius), density=True)
        return counts


# ------------------------------------------------------------------------

def load_chunks(w) -> List[Chunk]:
    chunks = []
    for file in sorted(os.listdir("./vis-data")):
        data = np.load(f"./vis-data/{file}")
        label = file.split("-")[1]
        if label != "undamaged":
            label = "damaged"
        print(file)
        chunk = Chunk(data, label, w)
        chunks.append(chunk)
    return chunks


def get_global_max_radius(chunks: List[Chunk], projected: bool):
    max_radius = 0
    for chunk in chunks:
        max_radius = max(max_radius, chunk.get_max_radius(projected))
    return max_radius

def compute_mahalanobis(points, query):
    mean = np.mean(points, axis=0)
    cov_matrix = np.cov(points, rowvar=False)

    # Inverse covariance
    inv_cov_matrix = np.linalg.inv(cov_matrix)

    # Method 1: Manual formula
    diff = query - mean
    mahalanobis_dist = np.sqrt(diff.T @ inv_cov_matrix @ diff)
    return mahalanobis_dist

def plot_mahalanobis(ax, labels, embeddings):
    s = 100
    x_min = np.min(embeddings[:, 0])
    x_max = np.max(embeddings[:, 0])
    y_min = np.min(embeddings[:, 1])
    y_max = np.max(embeddings[:, 1])

    # Compute ranges
    x_range = x_max - x_min
    y_range = y_max - y_min
    max_range = max(x_range, y_range)

    # Midpoints
    x_mid = (x_max + x_min) / 2
    y_mid = (y_max + y_min) / 2

    # Expand both axes to the same size
    x_min = x_mid - max_range / 2
    x_max = x_mid + max_range / 2
    y_min = y_mid - max_range / 2
    y_max = y_mid + max_range / 2

    x = np.linspace(x_min, x_max, s)
    y = np.linspace(y_min, y_max, s)
    X, Y = np.meshgrid(x, y)
    print(labels)
    cluster = np.array([e for idx, e in enumerate(embeddings) if labels[idx] == "undamaged"])
    print(cluster)

    coords = np.stack([X.ravel(), Y.ravel()], axis=-1)
    result = []
    for coord in coords:
        result.append(compute_mahalanobis(cluster, coord))
    result = np.array(result).reshape(s, s)
    print(result)
    im = ax.imshow(result, origin="lower", cmap="Blues_r", extent=[x_min, x_max, y_min, y_max])
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Mahalanobis distance", rotation=270, labelpad=15)

def plot_convex_hull(ax, labels, embeddings):
    cluster = np.array([e for idx, e in enumerate(embeddings) if labels[idx] == "undamaged"])
    hull = ConvexHull(cluster)
    for simplex in hull.simplices:
        ax.plot(cluster[simplex, 0], cluster[simplex, 1], '#43a047', alpha=0.7)


def compute_tsne_embedding(histograms):
    tsne = TSNE(
            n_components=2,
            initialization="random",
            random_state=1,
            metric=lambda p, q: jensenshannon(p, q),
            n_iter=1000
    )
    return tsne.fit(X=np.array(histograms))


def main():
    # chunks = load_chunks(100)
    # with open("temp.pickle", "wb") as f:
    #     pickle.dump(chunks, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('temp.pickle', 'rb') as f:
        chunks = pickle.load(f)
    max_radius = get_global_max_radius(chunks, False)
    histograms = np.array([c.get_histogram(False, max_radius) for c in chunks])
    embedding = compute_tsne_embedding(histograms)
    labels = [c.label for c in chunks]

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(10, 10)
    # plot_mahalanobis(ax, labels, embedding)
    plot_convex_hull(ax, labels, embedding)

    ax.scatter(
        embedding[:, 0],
        embedding[:, 1],
        c=[label_color_map[c.label] for c in chunks],
    )

    handles = [
        mpatches.Patch(color=color, label=label)
        for label, color in label_color_map.items()
    ]
    legend1 = ax.legend(handles=handles, labels=label_description_map.values(), loc="lower left")
    ax.add_artist(legend1)
    ax.set_title("Projected Bearings")

    plt.savefig(f"projection2.png", bbox_inches='tight', dpi=200)





if __name__ == '__main__':
    main()
