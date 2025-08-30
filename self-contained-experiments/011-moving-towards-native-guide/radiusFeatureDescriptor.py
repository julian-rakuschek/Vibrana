import copy
import os
from typing import List

import emd
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from openTSNE import affinity
from openTSNE import TSNE as TSNE2
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

    def swap_imf(self, imf, index):
        imfs = copy.deepcopy(self.emd)
        imfs[index] = imf
        return np.sum(imfs, axis=0)

def load_chunks(w) -> List[Chunk]:
    chunks = []
    for file in sorted(os.listdir("./vis-data")):
        data = np.load(f"./vis-data/{file}")
        label = file.split("-")[1]
        print(file)
        chunk = Chunk(data, label, w)
        chunks.append(chunk)
    return chunks

def get_global_max_radius(chunks: List[Chunk], projected: bool):
    max_radius = 0
    for chunk in chunks:
        max_radius = max(max_radius, chunk.get_max_radius(projected))
    return max_radius


def plot_reduction(ax, chunks: List[Chunk], cf_path: List[Chunk], projected: bool, global_max: bool, title: str):
    histograms = []
    max_radius = None
    labels = []
    merged = [*chunks, *cf_path]
    if global_max:
        max_radius = get_global_max_radius(merged, projected)
    for idx, chunk in enumerate(merged):
        histogram = chunk.get_histogram(projected, max_radius)
        histograms.append(histogram)
        if idx < len(chunks):
            labels.append(chunk.label)
    similarity_matrix = np.zeros((len(histograms), len(histograms)))

    for i, p in enumerate(histograms):
        for j, q in enumerate(histograms):
            similarity_matrix[i, j] = jensenshannon(p, q)
    # projected = MDS(n_components=2, dissimilarity="precomputed").fit_transform(similarity_matrix)
    projected = TSNE(n_components=2, metric="precomputed", init="random", random_state=1).fit_transform(similarity_matrix)
    scatter = ax.scatter(projected[:len(chunks), 0], projected[:len(chunks), 1], c=[label_map.index(l) for l in labels], cmap='rainbow')
    ax.plot(projected[len(chunks):, 0], projected[len(chunks):, 1], c="blue", marker="o")
    handles, legend_labels = scatter.legend_elements()
    legend1 = ax.legend(handles, label_map, loc="lower left", title="Classes")
    ax.add_artist(legend1)
    ax.set_title(title)
    ax.legend()

def main():
    chunks = load_chunks(100)
    plt.clf()
    fig, ax = plt.subplots(4, 1)
    fig.set_size_inches(10, 40)

    source = chunks[40]
    target = chunks[0]

    res = source.swap_imf(target.emd[0], 0)
    new_chunk = Chunk(res, "cf", 100)

    res2 = new_chunk.swap_imf(target.emd[0], 0)
    new_chunk_2 = Chunk(res2, "cf", 100)

    res3 = new_chunk_2.swap_imf(target.emd[0], 0)
    new_chunk_3 = Chunk(res3, "cf", 100)

    plot_reduction(ax[0], chunks, [], False, True, "Step 0")
    plot_reduction(ax[1], chunks, [source, new_chunk], False, True, "Step 1")
    plot_reduction(ax[2], chunks, [source, new_chunk, new_chunk_2], False, True, "Step 2")
    plot_reduction(ax[3], chunks, [source, new_chunk, new_chunk_2, new_chunk_3], False, True, "Step 3")
    plt.savefig(f"projectionExperiment.png", bbox_inches='tight', dpi=200)

def opentsne_trial():
    chunks = load_chunks(100)
    plt.clf()
    fig, ax = plt.subplots(2, 1)
    fig.set_size_inches(10, 20)

    histograms = []
    max_radius = get_global_max_radius(chunks, False)
    labels = []
    for idx, chunk in enumerate(chunks):
        histogram = chunk.get_histogram(False, max_radius)
        histograms.append(histogram)
        if idx < len(chunks):
            labels.append(chunk.label)
    similarity_matrix = np.zeros((len(histograms), len(histograms)))

    for i, p in enumerate(histograms):
        for j, q in enumerate(histograms):
            similarity_matrix[i, j] = jensenshannon(p, q)

    tsne = TSNE2(
        n_components=2,
        initialization="random",
        random_state=1,
        metric=lambda p, q: jensenshannon(p, q),
        n_iter=1000
    )

    projected = tsne.fit(X=np.array(histograms))
    ax[0].scatter(projected[:, 0], projected[:, 1], c=[label_map.index(l) for l in labels],
                         cmap='rainbow')

    source = chunks[40]
    target = chunks[0]

    res = source.swap_imf(target.emd[1], 1)
    new_chunk = Chunk(res, "cf", 100)

    new_embedding = projected.transform(np.array(new_chunk.get_histogram(projected=False, max_radius=max_radius)).reshape(1, -1))
    ax[1].scatter(projected[:, 0], projected[:, 1], c="red")
    ax[1].scatter(new_embedding[:, 0], new_embedding[:, 1], c="blue")

    plt.savefig(f"opentsne.png", bbox_inches='tight', dpi=200)

if __name__ == '__main__':
    opentsne_trial()