import numpy as np
from matplotlib import cm
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
from itertools import batched

from tslearn.piecewise import PiecewiseAggregateApproximation

from Experiment import Experiment
from util import find_nearest

class TakenMethod(Experiment):
    def __init__(
            self,
            experiment: str,
            name: str = "experiment",
            plot_rows: int = 1,
            plot_cols: int = 1,
            plot_fig_size: (int, int) or None = None,
            plot_mosaic: list or None = None,
            plot_title_font_size: int = 20,
            window_size: int = 2000
    ):
        super().__init__(experiment, name, plot_rows, plot_cols, plot_fig_size, plot_mosaic, plot_title_font_size)
        self.window_size = window_size
        self.windows = sliding_window_view(self.values, window_shape=window_size)
        self.projected = []

    def reduce(self, new_length, new_window_len):
        paa = PiecewiseAggregateApproximation(n_segments=new_length)
        step_size = len(self.values) // new_length
        self.values = paa.fit_transform(self.values.reshape(1, -1)).reshape(1, -1)[0]
        self.timestamps = [
            self.timestamps[window * step_size]
            for window in range(new_length)
        ]
        self.event_indices = [find_nearest(self.timestamps, e) for e in self.events]
        self.windows = sliding_window_view(self.values, window_shape=new_window_len)
        self.window_size = new_window_len

    def points_to_cloud(self, incremental=False):
        if incremental:
            print(len(self.windows))
            pca = IncrementalPCA(n_components=2, batch_size=1)
            for w in tqdm(batched(self.windows, 5000), total=len(self.windows) // 5000):
                if len(w) < 2:
                    continue
                pca.partial_fit(w)
            return pca.components_
        else:
            self.projected = PCA(n_components=2).fit_transform(self.windows)
            return self.projected

    def score_by_events(self):
        scores = []
        for idx, window in enumerate(self.windows):
            score = 0
            for event in self.event_indices:
                end_idx = idx + self.window_size
                if event < idx or event >= end_idx:
                    continue
                score = max((end_idx - event) / self.window_size, score)
            scores.append(score)
        return scores

    def score_by_radius(self, projected, norm=True):
        scores = []
        for point in projected:
            scores.append(np.linalg.norm(point))
        scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
        return scores_norm if norm else scores

    def plot_point_cloud(self, scores, s=5):
        row = "cloud" if self.plot_mosaic else 0
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        ax.set_axis_off()
        ax.set_xlim([np.min(self.projected[:, 0]), np.max(self.projected[:, 0])])
        ax.set_ylim([np.min(self.projected[:, 1]), np.max(self.projected[:, 1])])
        colors = cm.get_cmap('turbo')(scores)
        ax.scatter(self.projected[:, 0], self.projected[:, 1], s=s, c=colors)

    def plot_point_cloud_trace(self, start_i, end_i, s=5):
        print(start_i, end_i)
        row = "cloud" if self.plot_mosaic else 0
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        ax.set_axis_off()
        ax.set_xlim([np.min(self.projected[:, 0]), np.max(self.projected[:, 0])])
        ax.set_ylim([np.min(self.projected[:, 1]), np.max(self.projected[:, 1])])
        colors = [cm.get_cmap('turbo')((i - start_i) / (end_i - start_i)) if start_i <= i <= end_i else "lightgray" for i in range(len(self.windows))]
        ax.scatter(self.projected[:, 0], self.projected[:, 1], s=s, c=colors)
        ax.plot(self.projected[start_i:end_i+1, 0], self.projected[start_i:end_i+1, 1], c="black")

    def plot_point_curve(self, scores):
        row = "cloud" if self.plot_mosaic else 0
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        ax.set_axis_off()
        ax.set_xlim([np.min(self.projected[:, 0]), np.max(self.projected[:, 0])])
        ax.set_ylim([np.min(self.projected[:, 1]), np.max(self.projected[:, 1])])
        colors = cm.get_cmap('turbo')(scores)
        # for t in tqdm(range(self.projected.shape[0] - 1)):
        for t in tqdm(range(10)):
            ax.plot([self.projected[t, 0], self.projected[t, 1]], [self.projected[t + 1, 0], self.projected[t + 1, 1]], color=colors[t])
        ax.scatter(self.projected[:10, 0], self.projected[:10, 1], s=0.5, c=colors[:10])

    def plot_colored_signal(self, scores, title: str = "Raw Signal", include_events: bool = True):
        row = "raw" if self.plot_mosaic else 0
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        assert len(scores) == len(self.values)

        ax.set_title(title, fontsize=self.plot_title_font_size)
        ax.set_xlim(0, len(self.values))
        ax.xaxis.set_major_formatter(self.formatter)

        colors = cm.get_cmap('turbo')(scores)
        if include_events:
            ax.vlines(self.event_indices, 0, np.max(self.values), color="#ff4d4d", linewidth=1)
            ax.scatter(self.event_indices, np.tile(np.max(self.values), len(self.event_indices)), color="#ff4d4d", marker="v", s=60)
        for i in tqdm(range(len(self.values) - 1)):
            ax.plot([i, i+1], self.values[i:i+2], color=colors[i])


