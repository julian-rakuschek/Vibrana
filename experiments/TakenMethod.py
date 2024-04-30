import numpy as np
from matplotlib import cm
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

from Experiment import Experiment


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

    def points_to_cloud(self):
        pca = PCA(n_components=2)
        self.projected = pca.fit_transform(self.windows)
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

    def plot_point_cloud(self, scores):
        row = "cloud" if self.plot_mosaic else 0
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        ax.set_axis_off()
        ax.set_xlim([np.min(self.projected[:, 0]), np.max(self.projected[:, 0])])
        ax.set_ylim([np.min(self.projected[:, 1]), np.max(self.projected[:, 1])])
        colors = cm.get_cmap('turbo')(scores)
        ax.scatter(self.projected[:, 0], self.projected[:, 1], s=5, c=colors)

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


