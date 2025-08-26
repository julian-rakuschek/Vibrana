import os.path
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from sklearn.manifold import MDS, TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler

chunk_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "chunks", "fault-detection", "fault-detection-A")

def compute_tde(data, w):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)
    return projected

def main():
    time_series, tdes, classes = [], [], []
    N = len(os.listdir(chunk_folder))
    max_radius = 0
    for file in os.listdir(chunk_folder):
        values = np.load(os.path.join(chunk_folder, file))
        time_series.append(values)
        tde = compute_tde(values, w=1000)
        tdes.append(tde)
        label = file.split("-")[1]
        classes.append(1 if label == "undamaged" else 0)
        radii = np.linalg.norm(tde, axis=1)
        max_radius = max(max_radius, np.max(radii))
    histograms = []
    for tde in tdes:
        radii = np.linalg.norm(tde, axis=1)
        counts, bins = np.histogram(radii, bins=20, range=(0, max_radius), density=True)
        histograms.append(counts)

    similarity_matrix = np.zeros((N, N))
    for i, p in enumerate(histograms):
        for j, q in enumerate(histograms):
            similarity_matrix[i, j] = jensenshannon(p, q)
    print(similarity_matrix)

    # projected = MDS(n_components=2, dissimilarity="precomputed").fit_transform(similarity_matrix)
    projected = TSNE(n_components=2, metric="precomputed", init="random").fit_transform(similarity_matrix)
    plt.scatter(projected[:, 0], projected[:, 1], c=classes, cmap='rainbow')
    plt.savefig("projected.png")

if __name__ == '__main__':
    main()