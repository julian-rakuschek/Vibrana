import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from openTSNE import TSNE
from sklearn.preprocessing import StandardScaler
import matplotlib.patches as mpatches

label_color_map = {
    "inner": "#e91e63",
    "outer": "#ff9800",
    "undamaged": "#43a047",
}

label_description_map = {
    "inner": "Inner Damage",
    "outer": "Outer Damage",
    "undamaged": "Undamaged",
}

class Chunk:
    def __init__(self, data, label, w):
        self.data = data
        self.label = label
        self.w = w
        win = sliding_window_view(data, window_shape=w)
        self.windows = StandardScaler().fit_transform(win)
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
    if global_max:
        max_radius = get_global_max_radius(chunks, projected)
    for chunk in chunks:
        histogram = chunk.get_histogram(projected, max_radius)
        histograms.append(histogram)
    tsne = TSNE(
        n_components=2,
        initialization="random",
        random_state=1,
        metric=lambda p, q: jensenshannon(p, q),
        n_iter=1000
    )
    embedding = tsne.fit(X=np.array(histograms))
    ax.scatter(embedding[:, 0], embedding[:, 1], c=[label_color_map[c.label] for c in chunks], cmap='rainbow')

    handles = [
        mpatches.Patch(color=color, label=label)
        for label, color in label_color_map.items()
    ]
    legend1 = ax.legend(handles=handles, labels=label_description_map.values(), loc="lower left")
    ax.add_artist(legend1)
    ax.set_title(title)

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