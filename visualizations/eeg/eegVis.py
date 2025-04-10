import numpy as np
import polars as pl
from matplotlib import pyplot as plt
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from tqdm import tqdm
import matplotlib.dates as mdates

def slice_and_project(values, n_segments, title):
    window_size = len(values) // n_segments
    plot_mosaic = [
        ["line" for _ in range(n_segments)],
        [f"projection{i}" for i in range(n_segments)]
    ]
    fig, ax = plt.subplot_mosaic(plot_mosaic)
    fig.set_size_inches(10 * n_segments, 20)


    cuts = []
    arrow_locations = []
    for i in tqdm(range(n_segments)):
        if i != 0:
            cuts.append(i * window_size)
            arrow_locations.append((i * window_size + (i + 1) * window_size) // 2)
        subset = values[i * window_size:(i + 1) * window_size]
        windows = sliding_window_view(subset, window_shape=100)
        windows = StandardScaler().fit_transform(windows)
        projected = PCA(n_components=2).fit_transform(windows)

        scores = []
        for point in projected:
            scores.append(np.linalg.norm(point))
        scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

        ax[f"projection{i}"].set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
        ax[f"projection{i}"].set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
        ax[f"projection{i}"].scatter(projected[:, 0], projected[:, 1], s=15, c=colormaps["turbo"](scores_norm))
        ax[f"projection{i}"].axis("off")

    ax["line"].set_xlim(0, len(values))
    ax["line"].plot(values, color="black", linewidth=5)
    ax["line"].tick_params(axis='both', labelsize=50)
    ax["line"].vlines(cuts, ymin=np.min(values), ymax=np.max(values), color="#ff6361", linewidth=3)
    plt.savefig(title, bbox_inches='tight')



if __name__ == '__main__':
    # slice_and_project(pl.read_csv("eeg_Blinking.csv")["ch1"].to_numpy()[10000:], 23, title="eegBlinking.png")
    slice_and_project(pl.read_csv("eeg_teeth_clenching.csv")["ch1"].to_numpy()[100:18_000], 9, title="eegClenching.png")
