import numpy as np
import polars as pl
from matplotlib import pyplot as plt
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
import matplotlib.dates as mdates

def slice_and_project(df, channel, n_segments):
    channel_data = df[channel].to_numpy()
    window_size = len(channel_data) // n_segments
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
        subset = channel_data[i * window_size:(i + 1) * window_size]
        windows = sliding_window_view(subset, window_shape=2000)
        projected = PCA(n_components=2).fit_transform(windows)

        scores = []
        for point in projected:
            scores.append(np.linalg.norm(point))
        scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

        ax[f"projection{i}"].set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
        ax[f"projection{i}"].set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
        ax[f"projection{i}"].scatter(projected[:, 0], projected[:, 1], s=3, c=colormaps["turbo"](scores_norm))
        ax[f"projection{i}"].axis("off")

    ax["line"].set_title("Vibration Signal With Corresponding Time Delay Embeddings", fontsize=60)
    ax["line"].set_xlim(df["TimeStamp"][0], df["TimeStamp"][-1])
    ax["line"].plot(df["TimeStamp"], df[channel], color="black")
    tick_locs = df["TimeStamp"][cuts]
    ax["line"].set_xticks(tick_locs)
    date_format = mdates.DateFormatter("%Y-%m-%d %H:%M")
    ax["line"].xaxis.set_major_formatter(date_format)
    ax["line"].spines["top"].set_visible(False)
    ax["line"].spines["right"].set_visible(False)
    ax["line"].tick_params(axis='both', labelsize=50)
    ax["line"].vlines(tick_locs, ymin=np.min(channel_data), ymax=np.max(channel_data), color="#ff6361", linewidth=7)
    plt.savefig(f"{channel} projection paper", bbox_inches='tight')


def extract_slice(channel, start, length):
    df = pl.read_parquet("vibrationsdaten_Nov4-5_2022.parquet")
    df = df.slice(start, length)
    df = df.select(pl.col("TimeStamp", channel))
    df = df.select(["TimeStamp", channel])
    channel_mean = df.select(pl.mean(channel)).get_column(channel).item()

    if channel == "Ch1":
        df = df.with_columns(
            pl.when(pl.col(channel) > 0.5).then(channel_mean).otherwise(pl.col(channel)).alias(channel)
        )
    elif channel == "Ch2":
        df = df.with_columns(
            pl.when(pl.col(channel) > 100).then(channel_mean).otherwise(pl.col(channel)).alias(channel)
        )
        channel_mean = df.select(pl.mean(channel)).get_column(channel).item()
        df = df.with_columns(
            pl.when(pl.col(channel) > 0.15).then(channel_mean).otherwise(pl.col(channel)).alias(channel)
        )
    elif channel == "Ch3":
        df = df.with_columns(
            pl.when(pl.col(channel) < 8).then(channel_mean).otherwise(pl.col(channel)).alias(channel)
        )
    return df

if __name__ == '__main__':
    df = extract_slice("Ch1", 69_700_000, 1_100_000)
    slice_and_project(df, "Ch1", 10)
