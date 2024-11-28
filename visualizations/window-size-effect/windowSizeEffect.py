import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from matplotlib.collections import LineCollection

from parser.grav_waves import make_gravitational_waves

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

noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(1, snr=0.3)
values_a = noisy_signals_anomalous[0] * (10 ** 19)
values_a = MinMaxScaler().fit_transform(values_a.reshape(-1, 1)).reshape(1, -1)[0]
values_p = noisy_signals_plain[0] * (10 ** 19)
values_p = MinMaxScaler().fit_transform(values_p.reshape(-1, 1)).reshape(1, -1)[0]
values_g = gw_signals[0] * (10 ** 19)
values_g = MinMaxScaler().fit_transform(values_g.reshape(-1, 1)).reshape(1, -1)[0]


windows = sliding_window_view(values_p, window_shape=1_000)
projected = PCA(n_components=2).fit_transform(windows)
scores = []
for point in projected:
    scores.append(np.linalg.norm(point))
scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
ax["cloud2"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps["turbo"](scores_norm))
ax["cloud2"].axis("off")

segments = []
for i in range(len(values_p) - 1):
    segments.append([(i, values_p[i]), (i + 1, values_p[i + 1])])
lc = LineCollection(segments, cmap="turbo", linewidth=3)
lc.set_array(np.array(scores_norm))
# ax["line2"].plot(values_p, color="black", linewidth=3)
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
ax["cloud3"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps["turbo"](scores_norm))
ax["cloud3"].axis("off")

segments = []
for i in range(len(noisy_signals_anomalous[0]) - 1):
    segments.append([(i, noisy_signals_anomalous[0][i]), (i + 1, noisy_signals_anomalous[0][i + 1])])
lc = LineCollection(segments, cmap="turbo", linewidth=3)
lc.set_array(np.array(scores_norm))
# ax["line2"].plot(values_p, color="black", linewidth=3)
ax["line3"].add_collection(lc)
ax["line3"].set_title("The hidden signal (black) in the noise is revealed \n through the time delay embedding. Window Size = 1000", fontsize=title_font_size)

# ax["line3"].plot(noisy_signals_anomalous[0], color="black", linewidth=3)
ax["line3"].plot(gw_signals[0], color="black", linewidth=3)
ax["line3"].set_xlim(0, len(noisy_signals_anomalous[0]))
ax["line3"].spines["top"].set_visible(False)
ax["line3"].spines["right"].set_visible(False)



windows = sliding_window_view(values_a, window_shape=70)
projected = PCA(n_components=2).fit_transform(windows)
scores = []
for point in projected:
    scores.append(np.linalg.norm(point))
scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
ax["cloud4"].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps["turbo"](scores_norm))
ax["cloud4"].axis("off")

segments = []
for i in range(len(noisy_signals_anomalous[0]) - 1):
    segments.append([(i, noisy_signals_anomalous[0][i]), (i + 1, noisy_signals_anomalous[0][i + 1])])
lc = LineCollection(segments, cmap="turbo", linewidth=3)
lc.set_array(np.array(scores_norm))
# ax["line2"].plot(values_p, color="black", linewidth=3)
ax["line4"].add_collection(lc)
ax["line4"].set_title("The hidden signal (black) in the noise is revealed \n through the time delay embedding. Window Size = 70", fontsize=title_font_size)

# ax["line3"].plot(noisy_signals_anomalous[0], color="black", linewidth=3)
ax["line4"].plot(gw_signals[0], color="black", linewidth=3)
ax["line4"].set_xlim(0, len(noisy_signals_anomalous[0]))
ax["line4"].spines["top"].set_visible(False)
ax["line4"].spines["right"].set_visible(False)

plt.savefig(f"window-size-effect.png", bbox_inches='tight', dpi=200)
