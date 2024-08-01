import os.path
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.ticker as plticker
from tslearn.piecewise import PiecewiseAggregateApproximation

from util import find_nearest, derive_sample_rate


class Experiment:
    def __init__(
            self,
            experiment: str,
            name: str = "experiment",
            plot_rows: int = 1,
            plot_cols: int = 1,
            plot_fig_size: (int, int) or None = None,
            plot_mosaic: list or None = None,
            plot_title_font_size: int = 20
    ):
        self.experiment = experiment
        self.name = name
        self.data_path = f'{Path(__file__).parents[1]}/data/{experiment}'
        self.image_path = f'{Path(__file__).parents[1]}/images/{experiment}'
        self.plot_size = (plot_cols, plot_rows)
        self.plot_mosaic = plot_mosaic
        self.plot_title_font_size = plot_title_font_size

        # Attribute Check
        if not os.path.exists(self.data_path):
            raise AttributeError(f"Data path does exist not for {experiment}, please parse your dxd files")
        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path)
        for required_file in ["values.npy", "timestamps.npy", "event_timestamps.npy"]:
            if required_file not in os.listdir(self.data_path):
                raise AttributeError(f"{required_file} not found in {self.data_path}, please parse your dxd files")
        if plot_rows < 0 or plot_cols < 0:
            raise AttributeError("Invalid plot rows or columns")
        if plot_mosaic is not None and len(plot_mosaic) == 0:
            raise AttributeError("plot_mosaic must not be an empty list")
        if plot_fig_size is not None and len(plot_fig_size) != 2:
            raise AttributeError("plot_fig_size must be a Tuple with exactly two integers")

        # Data Loading
        self.values = np.load(f"{self.data_path}/values.npy")
        self.timestamps = np.load(f"{self.data_path}/timestamps.npy")
        self.events = np.load(f"{self.data_path}/event_timestamps.npy")
        self.event_indices = [find_nearest(self.timestamps, e) for e in self.events]
        self.sample_rate = derive_sample_rate(self.timestamps)

        # Plotting Setup
        plt.clf()
        if plot_mosaic:
            fig, ax = plt.subplot_mosaic(plot_mosaic)
        else:
            fig, ax = plt.subplots(nrows=plot_rows, ncols=plot_cols)
        self.fig, self.ax = fig, ax
        if plot_fig_size:
            self.fig.set_size_inches(*plot_fig_size)
        elif plot_mosaic:
            self.fig.set_size_inches((len(plot_mosaic[0]) * 30, len(plot_mosaic) * 10))
        else:
            self.fig.set_size_inches((plot_cols * 30, plot_rows * 10))
        self.formatter = plticker.FuncFormatter(lambda x_val, tick_pos: f"{x_val / self.sample_rate}s")

    def reduce(self, new_length):
        paa = PiecewiseAggregateApproximation(n_segments=new_length)
        step_size = len(self.values) // new_length
        self.values = paa.fit_transform(self.values.reshape(1, -1)).reshape(1, -1)[0]
        self.timestamps = [
            self.timestamps[window * step_size]
            for window in range(new_length)
        ]
        self.event_indices = [find_nearest(self.timestamps, e) for e in self.events]


    def plot_raw_signal(self, include_events: bool = True):
        row = "raw" if self.plot_mosaic else 0
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        ax.plot(np.arange(len(self.values)), self.values, color="black")
        ax.xaxis.set_major_formatter(self.formatter)
        ax.set_title("Raw Signal", fontsize=self.plot_title_font_size)
        ax.set_xlim([0, len(self.values)])
        if include_events:
            ax.vlines(self.event_indices, 0, np.max(self.values), color="#ff4d4d", linewidth=1)
            ax.scatter(self.event_indices, np.tile(np.max(self.values), len(self.event_indices)), color="#ff4d4d", marker="v", s=60)

    def plot_time_series(self, data: np.ndarray, row: int | str, title: str, include_events: bool = True, color: str = "indigo"):
        ax = self.ax if self.plot_size == (1, 1) and self.plot_mosaic is None else self.ax[row]
        ax.plot(data, color=color)
        ax.set_title(title, fontsize=self.plot_title_font_size)
        ax.set_xlim(0, len(self.values))
        ax.xaxis.set_major_formatter(self.formatter)
        if include_events:
            ax.vlines(self.event_indices, 0, np.max(data), color="#ff4d4d", linewidth=1)
            ax.scatter(self.event_indices, np.tile(np.max(data), len(self.event_indices)), color="#ff4d4d", marker="v", s=60)

    def plot_event_zoom(self, event: int, event_width: int = 15_000):
        if self.plot_mosaic != [["raw"], ["event"], ["event"]]:
            raise AttributeError('plot_mosaic must be initialized as [["raw"], ["event"], ["event"]]')
        event_index = self.event_indices[event]

        self.ax["raw"].plot(np.arange(len(self.values)), self.values, color="black")
        self.ax["raw"].set_xlim([0, len(self.values)])
        self.ax["raw"].set_title("Raw Signal", fontsize=self.plot_title_font_size)
        self.ax["raw"].xaxis.set_major_formatter(self.formatter)
        self.ax["raw"].axvspan(
            event_index, event_index + event_width,
            ymin=np.min(self.values), ymax=np.max(self.values),
            color='red', alpha=0.25)
        event_data = self.values[event_index:event_index + event_width]
        self.ax["event"].set_title("Zoomed Event", fontsize=self.plot_title_font_size)
        self.ax["event"].plot(np.arange(event_index, event_index + event_width), event_data, color="black")
        self.ax["event"].set_xlim([event_index, event_index + event_width])
        self.ax["event"].xaxis.set_major_formatter(self.formatter)

    def save(self):
        plt.savefig(f"{self.image_path}/{self.name}.png", bbox_inches='tight', dpi=200)


