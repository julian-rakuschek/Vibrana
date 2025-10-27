import copy
import itertools
import os
import pickle
import random
from typing import List, Self

import emd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from openTSNE import TSNE
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from tqdm import tqdm

label_color_map = {
    "inner": "#e91e63",
    "outer": "#ff9800",
    "undamaged": "#43a047",
    "counterfactual": "#304ffe"
}

label_description_map = {
    "inner": "Inner Damage",
    "outer": "Outer Damage",
    "undamaged": "Undamaged",
    "counterfactual": "Counterfactual Path"
}


# ------------------------------------------------------------------------

class Chunk:
    def __init__(self, data, label, w):
        self.data = data
        self.label = label
        self.w = w
        self.windows = sliding_window_view(data, window_shape=w)
        self.projected = PCA(n_components=2).fit_transform(self.windows)
        self.imfs = emd.sift.sift(data).T
        self.compute_ip_if_ia()

    def compute_ip_if_ia(self):
        IP, IF, IA = emd.spectra.frequency_transform(self.imfs, sample_rate=1.0, method='hilbert')
        self.average_ip = np.mean(IP, axis=0)
        self.average_if = np.mean(IF, axis=0)
        self.average_ia = np.mean(IA, axis=0)

    def ip_if_ia_distance(self, other: "Chunk", imf_index: int):
        vec1 = np.array([self.average_ia[imf_index], self.average_if[imf_index], self.average_ip[imf_index]])
        vec2 = np.array([other.average_ia[imf_index], other.average_if[imf_index], other.average_ip[imf_index]])
        return np.linalg.norm(vec1 - vec2)

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

def chunk_from_imfs(imfs, target_class, w) -> Chunk:
    data = np.sum(imfs, axis=0)
    chunk = Chunk(data, target_class, w)
    chunk.imfs = imfs
    chunk.compute_ip_if_ia()
    return chunk

# ------------------------------------------------------------------------

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

# ------------------------------------------------------------------------

class CounterfactualGenerator:
    def __init__(self, chunks: List[Chunk], source_idx: int, target_class: str, native_guides_count: int):
        count_target_class = len([c for c in chunks if c.label == target_class])

        if source_idx < 0 or source_idx >= len(chunks):
            raise ValueError(f"source_idx must be within [1, {len(chunks) - 1}]")

        if count_target_class == 0:
            raise ValueError(f"No points in target class found")

        if native_guides_count < 1 or native_guides_count > count_target_class:
            raise ValueError(f"native_guides_count must be within [1, {count_target_class}]")

        self.chunks = chunks
        self.max_radius = get_global_max_radius(self.chunks, False)
        self.source = chunks[source_idx]
        self.source_idx = source_idx
        self.target_class = target_class
        self.native_guides_count = native_guides_count
        self.native_guide = self.build_native_guide()
        self.interpolation_weights = self.init_interpolation_weights()

        labels = [c.label for c in chunks]
        histograms = np.array([c.get_histogram(False, self.max_radius) for c in chunks])
        self.model, self.label_encoder = train_classifier(histograms, labels)


    def build_native_guide(self) -> Chunk:
        distances = []
        source_hist = self.source.get_histogram(False, self.max_radius)
        for idx, c in enumerate(self.chunks):
            if c.label != self.target_class:
                continue
            hist = c.get_histogram(False, self.max_radius)
            dist = jensenshannon(source_hist, hist)
            distances.append((dist, idx))
        distances.sort(key=lambda s: s[0])
        native_guides = [self.chunks[d[1]] for d in distances[:self.native_guides_count]]
        native_guide_imfs = []
        for idx, source_imf in enumerate(self.source.imfs):
            level_imfs = []
            for ng in native_guides:
                if idx < len(ng.imfs):
                    level_imfs.append((ng.imfs[idx], ng.ip_if_ia_distance(self.source, idx)))
            level_imfs.sort(key=lambda s: s[1])
            native_guide_imfs.append(level_imfs[0][0])
        native_guide_imfs = np.array(native_guide_imfs)
        native_guide = chunk_from_imfs(native_guide_imfs, self.target_class, self.source.w)
        return native_guide

    def get_interpolate(self):
        interpolated_imfs = []
        for idx, w in enumerate(self.interpolation_weights):
            if idx < len(self.source.imfs) and idx < len(self.native_guide.imfs):
                interpolated = w["w_source"] * self.source.imfs[idx] + w["w_target"] * self.native_guide.imfs[idx] * w["w_target"]
                interpolated_imfs.append(interpolated)
        interpolated_imfs = np.array(interpolated_imfs)
        interpolate: Chunk = chunk_from_imfs(interpolated_imfs, "cf", self.source.w)
        label = self.model.predict(interpolate.get_histogram(False, self.max_radius).reshape(1, -1))
        interpolate.label = self.label_encoder.inverse_transform(label)[0]
        return interpolate

    def step_interpolation_weigths(self, step=0.05):
        # TODO implement advanced step mechanism based on variation
        for w in self.interpolation_weights:
            w["w_target"] = min(1, w["w_target"] + step)
            w["w_source"] = max(0, w["w_source"] - step)

    def init_interpolation_weights(self):
        max_imf_index = max(len(self.native_guide.imfs), len(self.source.imfs))
        weights = []
        for _ in range(max_imf_index):
            weights.append({"w_source": 1, "w_target": 0})
        return weights

    def visualize_current_step(self):
        color_source = "#311b92"
        color_source_imf = "#7e57c2"
        color_target = "#bf360c"
        color_target_imf = "#ff7043"
        interpolated = self.get_interpolate()
        is_target_class = interpolated.label == self.target_class
        color_interpolate = color_target if is_target_class else color_source
        color_interpolate_imf = color_target_imf if is_target_class else color_source_imf

        def plot_linechart(ax, data, color="black", title=""):
            ax.set_xlim([0, len(data)])
            ax.set_title(title, fontsize=30)
            ax.plot(data, color)

        def plot_tde(ax, data, w, color="black"):
            windows = sliding_window_view(data, window_shape=w)
            windows = StandardScaler().fit_transform(windows)
            projected = PCA(n_components=2).fit_transform(windows)
            ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
            ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
            ax.scatter(projected[:, 0], projected[:, 1], s=5, c=color)
            # ax.set_title(f"w = {w}", fontsize=30)
            ax.axis("off")

        def plot_interpolation_weights(ax, w1, w2):
            ax.barh(0, w1, color=color_source_imf, label=f'w1 = {w1:.1f}')
            ax.barh(0, w2, left=w1, color=color_target_imf, label=f'w2 = {w2:.1f}')
            ax.set_xlim(0, 1)
            ax.set_yticks([])

        def plot_summary_interpolation_weights(ax, weights):
            w1 = np.average([w["w_source"] for w in weights])
            w2 = np.average([w["w_target"] for w in weights])
            ax.barh(0, w1, color=color_source, label=f'w1 = {w1:.1f}')
            ax.barh(0, w2, left=w1, color=color_target, label=f'w2 = {w2:.1f}')
            ax.set_xlim(0, 1)
            ax.set_yticks([])

        rows = max(len(self.source.imfs), len(self.native_guide.imfs)) + 1
        mosaic = []
        for i in range(rows):
            src = [f"src_{i}", f"src_{i}", f"src_{i}", f"src_tde_{i}", f"src_tde_{i}"]
            cf_1 = [f"cf_{i}", f"cf_{i}", f"cf_{i}", f"cf_{i}", f"cf_tde_{i}"]
            cf_2 = [f"cf_ratio_{i}", f"cf_ratio_{i}", f"cf_ratio_{i}", f"cf_ratio_{i}", f"cf_ratio_{i}"]
            target = [f"target_{i}", f"target_{i}", f"target_{i}", f"target_tde_{i}", f"target_tde_{i}"]
            mosaic.append([*src, *cf_1, *target])
            mosaic.append([*src, *cf_2, *target])

        plt.clf()
        fig, ax = plt.subplot_mosaic(mosaic)
        fig.set_size_inches(40, 4 * rows)
        fig.subplots_adjust(hspace=1, wspace=1)
        for i in range(rows):
            if i == 0:
                plot_linechart(ax[f"src_{i}"], self.source.data, color_source, "Source")
                plot_linechart(ax[f"target_{i}"], self.native_guide.data, color_target, "Target")
                plot_linechart(ax[f"cf_{i}"], interpolated.data, color_interpolate, "Interpolate")
                plot_tde(ax[f"src_tde_{i}"], self.source.data, self.source.w, color_source)
                plot_tde(ax[f"target_tde_{i}"], self.native_guide.data, self.source.w, color_target)
                plot_tde(ax[f"cf_tde_{i}"], interpolated.data, self.source.w, color_interpolate)
                plot_summary_interpolation_weights(ax[f"cf_ratio_{0}"], self.interpolation_weights)
            else:
                imf_idx = i - 1
                if imf_idx < len(self.source.imfs):
                    plot_linechart(ax[f"src_{i}"], self.source.imfs[imf_idx], color_source_imf, f"Source IMF {imf_idx}")
                    plot_tde(ax[f"src_tde_{i}"], self.source.imfs[imf_idx], self.source.w, color_source_imf)
                if imf_idx < len(self.native_guide.imfs):
                    plot_linechart(ax[f"target_{i}"], self.native_guide.imfs[imf_idx], color_target_imf, f"Target IMF {imf_idx}")
                    plot_tde(ax[f"target_tde_{i}"], self.native_guide.imfs[imf_idx], self.source.w, color_target_imf)
                if imf_idx < len(self.source.imfs) and imf_idx < len(self.native_guide.imfs):
                    plot_linechart(ax[f"cf_{i}"], interpolated.imfs[imf_idx], color_interpolate_imf, f"Interpolate IMF {imf_idx}")
                    plot_tde(ax[f"cf_tde_{i}"], interpolated.imfs[imf_idx], self.source.w, color_interpolate_imf)
                    plot_interpolation_weights(ax[f"cf_ratio_{i}"], self.interpolation_weights[imf_idx]["w_source"], self.interpolation_weights[imf_idx]["w_target"])
        plt.savefig("step.png", bbox_inches='tight', dpi=200)
        plt.close(fig)



# ------------------------------------------------------------------------


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


def main():
    chunks = load_chunks(100)
    # with open("temp.pkl", "wb") as f:
    #     pickle.dump(chunks, f)
    # with open("temp.pkl", "rb") as f:
    #     chunks = pickle.load(f)
    gen = CounterfactualGenerator(chunks, 0, "undamaged", 3)
    gen.step_interpolation_weigths(step=0.95)
    gen.visualize_current_step()



if __name__ == '__main__':
    main()
