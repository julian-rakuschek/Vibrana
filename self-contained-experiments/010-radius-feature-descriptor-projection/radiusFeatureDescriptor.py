import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

label_map = ["inner", "outer", "undamaged"]

class Chunk:
    def __init__(self, data, label, w):
        self.data = data
        self.label = label
        self.w = w
        self.windows = sliding_window_view(data, window_shape=w)
        self.projected = PCA(n_components=2).fit_transform(self.windows)

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

def load_chunks(w):
    chunks = []
    for file in os.listdir("./vis-data"):
        data = np.load(f"./vis-data/{file}")
        label = file.split("-")[1]
        chunk = Chunk(data, label, w)
        chunks.append(chunk)
    return chunks

def get_global_max_radius(chunks: List[Chunk], projected: bool):
    max_radius = 0
    for chunk in chunks:
        max_radius = max(max_radius, chunk.get_max_radius(projected))
    return max_radius

def plot_reduction(ax, chunks: List[Chunk], projected: bool, global_max: bool, title: str):
    histograms = []
    max_radius = None
    labels = []
    if global_max:
        max_radius = get_global_max_radius(chunks, projected)
    for chunk in chunks:
        histogram = chunk.get_histogram(projected, max_radius)
        histograms.append(histogram)
        labels.append(chunk.label)
    similarity_matrix = np.zeros((len(histograms), len(histograms)))

    for i, p in enumerate(histograms):
        for j, q in enumerate(histograms):
            similarity_matrix[i, j] = jensenshannon(p, q)
    # projected = MDS(n_components=2, dissimilarity="precomputed").fit_transform(similarity_matrix)
    projected = TSNE(n_components=2, metric="precomputed", init="random").fit_transform(similarity_matrix)
    scatter = ax.scatter(projected[:, 0], projected[:, 1], c=[label_map.index(l) for l in labels], cmap='rainbow')
    handles, legend_labels = scatter.legend_elements()
    print(legend_labels)
    legend1 = ax.legend(handles, label_map, loc="lower left", title="Classes")
    ax.add_artist(legend1)
    ax.set_title(title)
    ax.legend()

def main():
    chunks = load_chunks(100)
    plt.clf()
    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(20, 20)
    plot_reduction(ax[0, 0], chunks, True, True, "Sliding windows with PCA | Global maximum radius")
    plot_reduction(ax[0, 1], chunks, True, False, "Sliding windows with PCA | Local maximum radius")
    plot_reduction(ax[1, 0], chunks, False, True, "Sliding windows without PCA | Global maximum radius")
    plot_reduction(ax[1, 1], chunks, False, False, "Sliding windows without PCA | Local maximum radius")
    plt.savefig(f"projectionExperiment.png", bbox_inches='tight', dpi=200)

if __name__ == '__main__':
    main()