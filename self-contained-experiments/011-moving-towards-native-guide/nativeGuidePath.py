import copy
import itertools
import os
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler
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

    def get_candidates(self, target: Self):
        candidates = []
        imf_count = min(self.emd.shape[0], target.emd.shape[0])
        for i in range(imf_count):
            target_imf = target.emd[i]
            swapped = self.swap_imf(target_imf, i)
            candidates.append(swapped)
        return candidates


# ------------------------------------------------------------------------

class CounterfactualGenerator:
    def __init__(self, chunks: List[Chunk], source_idx: int, target_class: str, strategy: str, native_guides_count: int):
        count_target_class = len([c for c in chunks if c.label == target_class])
        valid_strategies = ["first", "middle", "last", "random", "effect"]

        if source_idx < 0 or source_idx >= len(chunks):
            raise ValueError(f"source_idx must be within [1, {len(chunks) - 1}]")

        if count_target_class == 0:
            raise ValueError(f"No points in target class found")

        if native_guides_count < 1 or native_guides_count > count_target_class:
            raise ValueError(f"native_guides_count must be within [1, {count_target_class}]")

        if strategy not in valid_strategies:
            raise ValueError(f"strategy {strategy} is not an available strategy. Possible values for strategy are: {','.join(valid_strategies)}")

        self.chunks = chunks
        self.source = chunks[source_idx]
        self.source_idx = source_idx
        self.target_class = target_class
        self.strategy = strategy
        self.native_guides_count = native_guides_count
        self.max_radius = get_global_max_radius(self.chunks, False)
        self.native_guide_indices = self.select_native_guides(native_guides_count)
        self.native_guides = [self.chunks[i] for i in self.native_guide_indices]
        self.embedding = self.compute_tsne_embedding()
        self.cf_path: List[Chunk] = [self.source]
        self.imf_swaps = []
        self.chosen_native_guides = []

    def select_native_guides(self, count):
        distances = []
        source_hist = self.source.get_histogram(False, self.max_radius)
        for idx, c in enumerate(self.chunks):
            if c.label != self.target_class:
                continue
            hist = c.get_histogram(False, self.max_radius)
            dist = jensenshannon(source_hist, hist)
            distances.append((dist, idx))
        distances.sort(key=lambda s: s[0])
        return [d[1] for d in distances[:count]]

    def compute_tsne_embedding(self):
        histograms = [c.get_histogram(False, self.max_radius) for c in self.chunks]
        tsne = TSNE(
            n_components=2,
            initialization="random",
            random_state=1,
            metric=lambda p, q: jensenshannon(p, q),
            n_iter=1000
        )
        return tsne.fit(X=np.array(histograms))

    def plot_chunk_embedding(self, ax, title=""):
        ax.scatter(
            self.embedding[:, 0],
            self.embedding[:, 1],
            c=[label_color_map[c.label] for c in self.chunks],
        )
        # Plot Native Guide as star
        for i in self.native_guide_indices:
            ax.scatter(
                self.embedding[i, 0],
                self.embedding[i, 1],
                c=label_color_map["counterfactual"],
                marker="*",
                s=100
            )

        handles = [
            mpatches.Patch(color=color, label=label)
            for label, color in label_color_map.items()
        ]
        legend1 = ax.legend(handles=handles, labels=label_description_map.values(), loc="lower left")
        ax.add_artist(legend1)
        ax.set_title(title)

    def plot_counterfactual_path(self, ax):
        histograms = [c.get_histogram(False, self.max_radius) for c in self.cf_path]
        histograms = np.array(histograms)
        embedded = self.embedding[self.source_idx].reshape(1, -1)
        if len(self.cf_path) > 1:
            embedded = np.concat([embedded, self.embedding.transform(histograms[1:])], axis=0)
        ax.plot(embedded[:, 0], embedded[:, 1], c=label_color_map["counterfactual"], marker="o")

    def generate_cf_candidate(self, source: Chunk, target: Chunk):
        candidates = source.get_candidates(target)
        candidates = [Chunk(c, None, source.w) for c in candidates]

        if self.strategy == "first":
            return candidates[0], 0
        if self.strategy == "middle":
            middle_idx = len(candidates) // 2
            return candidates[middle_idx], middle_idx
        if self.strategy == "last":
            return candidates[-1], -1
        if self.strategy == "random":
            i = random.choice(range(len(candidates)))
            return candidates[i], i

        histograms = [c.get_histogram(False, self.max_radius) for c in candidates]
        target_hist = target.get_histogram(False, self.max_radius)
        distances = [jensenshannon(p, target_hist) for p in histograms]
        return candidates[np.argmin(distances)], np.argmin(distances)

    def cf_step(self):
        native_guide = random.choice(self.native_guides)
        cf, imf_idx = self.generate_cf_candidate(self.cf_path[-1], native_guide)
        self.cf_path.append(cf)
        self.imf_swaps.append(imf_idx)
        self.chosen_native_guides.append(native_guide)

    def visualize_cf_step(self, step: int, folder: str):
        if step < 1 or step >= len(self.cf_path):
            raise ValueError(f"step must be within [1, {len(self.cf_path) - 1}]")
        step_a = self.cf_path[step - 1]
        step_b = self.cf_path[step]
        native_guide = self.chosen_native_guides[step - 1]

        max_imf_count = np.max([step_a.emd.shape[0], step_b.emd.shape[0], native_guide.emd.shape[0]])

        plt.clf()
        fig, ax = plt.subplots(ncols=6, nrows=1 + max_imf_count)
        fig.set_size_inches(30, (max_imf_count + 1) * 5)

        plot_emd_result(ax, 0, 1, step_a, f"Step {step - 1}" if step - 1 != 0 else "Source", swapped_imf_idx=self.imf_swaps[step - 1])
        plot_emd_result(ax, 2, 3, step_b, f"Step {step}", swapped_imf_idx=self.imf_swaps[step - 1])
        plot_emd_result(ax, 4, 5, native_guide, "Native Guide", swapped_imf_idx=self.imf_swaps[step - 1])

        os.makedirs(folder, exist_ok=True)
        file = os.path.join(folder, f"emd_step_{step}.png")
        plt.savefig(file, bbox_inches='tight', dpi=200)
        plt.close(fig)

    def visualize_cf_path(self, step: int, folder: str = "."):
        plt.clf()
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches(10, 10)

        self.plot_chunk_embedding(ax, f"Step {step}")
        self.plot_counterfactual_path(ax)
        os.makedirs(folder, exist_ok=True)
        file = os.path.join(folder, f"path_step_{step}.png")
        plt.savefig(file, bbox_inches='tight', dpi=200)
        plt.close(fig)

    def visualize_possible_candidates(self):
        plt.clf()
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches(10, 10)
        self.plot_chunk_embedding(ax, f"Possible Candidates")
        candidates = self.source.get_candidates(self.native_guides[0])
        candidates = [Chunk(c, None, self.source.w) for c in candidates]
        histograms = [c.get_histogram(False, self.max_radius) for c in candidates]
        histograms = np.array(histograms)
        embedded = self.embedding.transform(histograms)

        ax.scatter(embedded[:, 0], embedded[:, 1], c=label_color_map["counterfactual"], marker="o")
        s = self.embedding[self.source_idx]
        for e in embedded:
            ax.plot([s[0], e[0]], [s[1], e[1]], c=label_color_map["counterfactual"], linewidth=0.8)

        plt.savefig("best_candidate.png", bbox_inches='tight', dpi=200)
        plt.close(fig)


# ------------------------------------------------------------------------

def plot_time_series(ax, data: np.ndarray, title: str, color: str = "indigo"):
    ax.plot(data, color=color)
    ax.set_title(title, fontsize=20)
    ax.set_xlim(0, len(data))


def plot_tde_projection(ax, data, w, monochrome=None):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)

    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    ax.scatter(projected[:, 0], projected[:, 1], s=5, c=monochrome if monochrome is not None else plt.colormaps["turbo"](scores_norm))
    # ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")


def plot_emd_result(ax, column_ts, column_projected, chunk: Chunk, title, w=100, swapped_imf_idx=0):
    plot_time_series(ax[0, column_ts], chunk.data, title, "black")
    plot_tde_projection(ax[0, column_projected], chunk.data, w)
    unchanged_color = "#c5cae9"
    swapped_color = "#3d5afe"
    for i in range(chunk.emd.shape[0]):
        plot_time_series(ax[i + 1, column_ts], chunk.emd[i, :], f"IMF {i}", swapped_color if i == swapped_imf_idx else unchanged_color)
        plot_tde_projection(ax[i + 1, column_projected], chunk.emd[i, :], w)


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


def main(chunks: List[Chunk] = None, steps: int = 4, strategy: str = "effect", native_guides: int = 1, plot_emd_step: bool = True):
    print(f"Steps = {steps}, Strategy = {strategy}, Native Guides = {native_guides}")
    if chunks is None:
        chunks = load_chunks(100)
    folder = f"{strategy}-NG{native_guides}"
    generator = CounterfactualGenerator(chunks, 0, "undamaged", strategy, native_guides)
    generator.visualize_cf_path(0, folder)

    for s in tqdm(range(1, steps + 1)):
        generator.cf_step()
        generator.visualize_cf_path(s, folder)
        if plot_emd_step:
            generator.visualize_cf_step(s, folder)

def experiment_all_strategies():
    chunks = load_chunks(100)
    valid_strategies = ["first", "middle", "last", "random", "effect"]
    native_guides = [1, 2, 3]
    for strategy, ng in itertools.product(valid_strategies, native_guides):
        main(chunks=chunks, steps=30, strategy=strategy, native_guides=ng, plot_emd_step=False)

def plot_best_candidates():
    chunks = load_chunks(100)
    generator = CounterfactualGenerator(chunks, 0, "undamaged", "effect", 1)
    generator.visualize_possible_candidates()

if __name__ == '__main__':
    plot_best_candidates()
