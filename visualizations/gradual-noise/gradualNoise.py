import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import ShortTimeFFT, get_window
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

noise_iterations = 10
noise_row_selection = [0, 1, 5, 8]
w = 200
plot_mosaic = [
    [f"values{i}", f"values{i}", f"TDE{i}", f"spectro{i}"] for i in range(len(noise_row_selection))
]

fig, ax = plt.subplot_mosaic(plot_mosaic)
plt.subplots_adjust(wspace=0.1, hspace=0.3)
fig.set_size_inches(30, 5 * len(noise_row_selection))

values = np.load("motor-clean.npy")

for i in range(noise_iterations):
    if i not in noise_row_selection:
        values += 1 * np.random.randn(len(values))
        continue
    plot_row = noise_row_selection.index(i)
    windows = sliding_window_view(values, window_shape=w)
    projected = PCA(n_components=2).fit_transform(windows)

    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
    ax[f"TDE{plot_row}"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps["turbo"](scores_norm))
    ax[f"TDE{plot_row}"].axis("off")
    ax[f"TDE{plot_row}"].set_title(f"TDE", fontsize=30)

    scores_ts = np.concatenate([np.repeat(scores_norm[0], w // 2), scores_norm, np.repeat(scores_norm[-1], w // 2)])

    segments = []
    for j in range(len(values) - 1):
        segments.append([(j, values[j]), (j + 1, values[j + 1])])
    lc = LineCollection(segments, cmap="turbo", linewidth=1)
    lc.set_array(np.array(scores_ts))
    ax[f"values{plot_row}"].add_collection(lc)
    ax[f"values{plot_row}"].set_xlim(0, len(values))
    ax[f"values{plot_row}"].set_ylim(np.min(values), np.max(values))
    ax[f"values{plot_row}"].set_title(f"Noise Iteration {i}", fontsize=30)

    window = get_window('hann', 300)
    SFT = ShortTimeFFT(window, hop=100, fs=10_000, mfft=None, scale_to="psd")
    Sx = SFT.spectrogram(values)
    Sx[Sx > np.percentile(Sx, 95)] = np.percentile(Sx, 95)
    ax[f"spectro{plot_row}"].imshow(Sx, origin='lower', aspect='auto', extent=SFT.extent(len(values)), cmap='viridis')
    ax[f"spectro{plot_row}"].get_xaxis().set_visible(False)
    ax[f"spectro{plot_row}"].set_title(f"Spectrogram", fontsize=30)
    values += 1 * np.random.randn(len(values))

plt.savefig(f"gradual-noise-2.png", bbox_inches='tight', dpi=50)