import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from matplotlib.collections import LineCollection

cmap = "jet"

plot_mosaic = [
    ["line1", "line1", "cloud1"],
    ["line2", "line2", "cloud2"],
    ["line3", "line3", "cloud3"],
    ["line4", "line4", "cloud4"],
]

fig, ax = plt.subplot_mosaic(plot_mosaic)
plt.subplots_adjust(wspace=0.1, hspace=0.5)
fig.set_size_inches(20, 25)
title_font_size = 30
n_samples = 1_000
sine_wave = [np.sin((i / n_samples) * 100) for i in range(n_samples)]

ax["line1"].plot(sine_wave, color="black", linewidth=3)
ax["line1"].set_xlim(0, len(sine_wave))
ax["line1"].set_title("Harmonic oscillations result in a circle", fontsize=title_font_size)
ax["line1"].spines["top"].set_visible(False)
ax["line1"].spines["right"].set_visible(False)
windows = sliding_window_view(sine_wave, window_shape=50)
projected = PCA(n_components=2).fit_transform(windows)
ax["cloud1"].scatter(projected[:, 0], projected[:, 1], s=8, c="black")
ax["cloud1"].axis("off")

values_a = np.load("values-signal-in-noise.npy")
values_p = np.load("values-noise.npy")
values_g = np.load("values-signal-to-embed.npy")

windows = sliding_window_view(values_p, window_shape=1_000)
projected = PCA(n_components=2).fit_transform(windows)
scores = []
for point in projected:
    scores.append(np.linalg.norm(point))
scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
ax["cloud2"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps[cmap](scores_norm))
ax["cloud2"].axis("off")

segments = []
for i in range(len(values_p) - 1):
    segments.append([(i, values_p[i]), (i + 1, values_p[i + 1])])
lc = LineCollection(segments, cmap=cmap, linewidth=3)
lc.set_array(np.array(scores_norm))
ax["line2"].add_collection(lc)
ax["line2"].set_xlim(0, len(values_p))
ax["line2"].set_title("Pure noise results in a point cloud \n without structures / patterns", fontsize=title_font_size)
ax["line2"].spines["top"].set_visible(False)
ax["line2"].spines["right"].set_visible(False)



windows = sliding_window_view(values_a, window_shape=1_000)
projected = PCA(n_components=2).fit_transform(windows)
scores = []
for point in projected:
    scores.append(np.linalg.norm(point))
scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
ax["cloud3"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps[cmap](scores_norm))
ax["cloud3"].axis("off")

segments = []
for i in range(len(values_a) - 1):
    segments.append([(i, values_a[i]), (i + 1, values_a[i + 1])])
lc = LineCollection(segments, cmap=cmap, linewidth=3)
lc.set_array(np.array(scores_norm))
ax["line3"].add_collection(lc)
ax["line3"].set_title("The hidden signal (black) in the noise is revealed \n through the time delay embedding. Window Size = 1000", fontsize=title_font_size)

ax["line3"].plot(values_g, color="black", linewidth=3)
ax["line3"].set_xlim(0, len(values_a))
ax["line3"].spines["top"].set_visible(False)
ax["line3"].spines["right"].set_visible(False)



windows = sliding_window_view(values_a, window_shape=70)
projected = PCA(n_components=2).fit_transform(windows)
scores = []
for point in projected:
    scores.append(np.linalg.norm(point))
scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
ax["cloud4"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps[cmap](scores_norm))
ax["cloud4"].axis("off")

segments = []
for i in range(len(values_a) - 1):
    segments.append([(i, values_a[i]), (i + 1, values_a[i + 1])])
lc = LineCollection(segments, cmap=cmap, linewidth=3)
lc.set_array(np.array(scores_norm))
ax["line4"].add_collection(lc)
ax["line4"].set_title("The hidden signal (black) in the noise is revealed \n through the time delay embedding. Window Size = 70", fontsize=title_font_size)

ax["line4"].plot(values_g, color="black", linewidth=3)
ax["line4"].set_xlim(0, len(values_a))
ax["line4"].spines["top"].set_visible(False)
ax["line4"].spines["right"].set_visible(False)

plt.savefig(f"window-size-effect-{cmap}.png", bbox_inches='tight', dpi=200)
