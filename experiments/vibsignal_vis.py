import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA

data = np.load("C:\\Users\\jrakusch\\Coding\\present-binder-use-case\\data\\samples\\5-10-1t-10-16\\abnormal-0000\\values.npy")
data = data[13_000:14_200]
print(data)

fig, ax = plt.subplots(nrows=1, ncols=2)
fig.set_size_inches(30, 10)
ax[0].set_xlim([0, len(data)])
ax[0].axis('off')
ax[0].plot(data, color="black")


windows = sliding_window_view(data, window_shape=800)
projected = PCA(n_components=2).fit_transform(windows)
ax[1].scatter(projected[:, 0], projected[:, 1], c="black")
ax[1].axis('off')
plt.savefig("test.png", bbox_inches='tight')