import os
from pathlib import Path
from matplotlib import cm
import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

values = np.load(os.path.join(Path(__file__).parents[1], "data", "5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt", "values.npy"))

fig, ax = plt.subplots(nrows=1, ncols=1)
fig.set_size_inches(30, 10)
ax.set_xlim([0, len(values)])
ax.axis('off')
ax.plot(values, color="black")
plt.savefig("line2.png", bbox_inches='tight')

windows = sliding_window_view(values, window_shape=2000)
projected = PCA(n_components=2).fit_transform(windows)
scores = []
for point in projected:
    scores.append(np.linalg.norm(point))
scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
colors = cm.get_cmap('turbo')(scores_norm)

plt.clf()
fig, ax = plt.subplots(nrows=1, ncols=1)
fig.set_size_inches(30, 30)
ax.scatter(projected[:, 0], projected[:, 1], c=colors)
ax.axis('off')
plt.savefig("projected2.png", bbox_inches='tight')
