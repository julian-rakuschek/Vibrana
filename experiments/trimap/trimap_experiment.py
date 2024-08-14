import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap, MDS
import umap
import trimap
from gudhi.clustering.tomato import Tomato

window_size = 500
values = np.load("values.npy")
values = values[80_000:950_000]
windows = sliding_window_view(values, window_shape=window_size)[::window_size]
ffts = [np.fft.fft(w) for w in windows]
distances = [[np.linalg.norm(ffts[i] - ffts[j]) for j in range(len(windows))] for i in range(len(windows))]
embedding = MDS(dissimilarity="precomputed").fit_transform(distances)
fig, ax = plt.subplots(nrows=1, ncols=1)
fig.set_size_inches((20, 20))
ax.scatter(embedding[:, 0], embedding[:, 1], marker='.', s=10)
plt.show()

# t = Tomato(density_type='KDE', k=5)
# t.n_clusters_ = 2
# labels = t.fit_predict(windows)
#
#
# print(len(windows))
# embedding = Isomap().fit_transform(windows)
# # embedding = PCA().fit_transform(windows)
# # embedding = trimap.TRIMAP(verbose=True).fit_transform(windows)
#
# print(embedding)
# fig, ax = plt.subplots(nrows=1, ncols=1)
# fig.set_size_inches((20, 20))
# ax.scatter(embedding[:, 0], embedding[:, 1], marker='.', s=5, c=labels)
# plt.show()
#
# np.save("embedding.npy", embedding)
