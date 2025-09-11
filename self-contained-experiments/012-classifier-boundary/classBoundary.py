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
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from umap import UMAP

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


def train_classifier(histograms, labels):
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    model = make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=1)
    )
    model.fit(histograms, y)

    # Compute training accuracy
    preds = model.predict(histograms)
    acc = accuracy_score(y, preds)
    print(f"Training accuracy: {acc:.2f}")

    return model, label_encoder

def plot_dbm(ax, model, umap_embedding, embeddings):
    s = 100
    x_min = np.min(embeddings[:, 0])
    x_max = np.max(embeddings[:, 0])
    y_min = np.min(embeddings[:, 1])
    y_max = np.max(embeddings[:, 1])

    x = np.linspace(x_min, x_max, s)
    y = np.linspace(y_min, y_max, s)
    X, Y = np.meshgrid(x, y)

    coords = np.stack([X.ravel(), Y.ravel()], axis=-1)
    print(coords)
    inverse = umap_embedding.inverse_transform(coords)
    preds = model.predict(inverse)
    result = preds.reshape(s, s)
    print(result)
    cmap = ListedColormap(["#e91e63", "#43a047"])
    ax.imshow(result, origin="lower", cmap=cmap, extent=[x_min, x_max, y_min, y_max], alpha=0.2)

def main():
    # chunks = load_chunks(100)
    # with open("temp.pickle", "wb") as f:
    #     pickle.dump(chunks, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('temp.pickle', 'rb') as f:
        chunks = pickle.load(f)
    max_radius = get_global_max_radius(chunks, False)
    histograms = np.array([c.get_histogram(False, max_radius) for c in chunks])
    # embedding_model = UMAP(metric="euclidean", random_state=42).fit(histograms)
    # embedding = embedding_model.transform(histograms)
    embedding_model = PCA(n_components=2)
    embedding_model.fit(histograms)
    embedding = embedding_model.fit_transform(histograms)
    labels = [c.label for c in chunks]
    model, label_encoder = train_classifier(histograms, labels)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(10, 10)
    plot_dbm(ax, model, embedding_model, embedding)

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
    ax.legend()

    plt.savefig(f"projection.png", bbox_inches='tight', dpi=200)





if __name__ == '__main__':
    main()
