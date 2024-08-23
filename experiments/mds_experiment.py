import itertools
import os
import random

import matplotlib.pyplot as plt

# unused but required import for doing 3d projections with matplotlib < 3.2
import mpl_toolkits.mplot3d  # noqa: F401
import numpy as np
from fastdtw import fastdtw
from joblib import Parallel, delayed
from matplotlib import ticker
from numpy.lib.stride_tricks import sliding_window_view
from scipy.spatial import distance
from sklearn import datasets, manifold
from sklearn.preprocessing import MinMaxScaler

from algorithms.lmds import landmark_MDS


def plot_2d(ax, points, points_color, title):
    x, y = points.T
    if points_color is None:
        ax.scatter(x, y, s=50, alpha=0.8)
    else:
        ax.scatter(x, y, c=points_color, s=50, alpha=0.8)
    ax.set_title(title)
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_major_formatter(ticker.NullFormatter())


def toy_example():
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(3, 3), facecolor="white", constrained_layout=True)
    fig.set_size_inches((40, 20))
    n_samples = 1500
    S_points, S_color = datasets.make_s_curve(n_samples, random_state=0)

    lle_mod = manifold.MDS()
    S_mds = lle_mod.fit_transform(S_points)
    print(S_mds)
    plot_2d(ax[0], S_mds, S_color, "MDS")


    lands = random.sample(range(0, S_points.shape[0], 1), 10)
    lands = np.array(lands, dtype=int)
    Dl2 = distance.cdist(S_points[lands, :], S_points, 'euclidean')
    xl_2 = landmark_MDS(Dl2, lands, 2)
    print(xl_2)
    plot_2d(ax[1], xl_2, S_color, "LMDS")
    plt.show()

def dtw_matrix(tsData):
    parsed = [MinMaxScaler().fit_transform(item.reshape(-1, 1)).reshape(1, -1)[0] for item in tsData]
    num_anomalies = len(parsed)
    indices = [idx for idx in itertools.product(range(num_anomalies), repeat=2) if idx[1] > idx[0]]
    dtw_values = Parallel(n_jobs=os.cpu_count())(
        delayed(lambda index: (fastdtw(parsed[index[0]], parsed[index[1]], dist=2)[0], index))(idx) for idx in indices)
    y = np.zeros((num_anomalies, num_anomalies))
    for item in dtw_values:
        y[item[1][0], item[1][1]] = item[0]
    y = y + y.T - np.diag(y.diagonal())
    return y

def dicker_fisch():
    path = "C:\\Users\\jrakusch\\Coding\\present-binder-use-case\\data\\samples\\dummy\\0001\\values.npy"
    path2 = "C:\\Users\\jrakusch\\Coding\\present-binder-use-case\\data\\5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1 t pro h\\values.npy"
    values = np.load(path)
    windows = sliding_window_view(values, window_shape=2000)
    lands = random.sample(range(0, windows.shape[0], 1), 200)
    lands = np.array(lands, dtype=int)
    Dl2 = distance.cdist(windows[lands, :], windows, 'chebyshev')

    xl_2 = landmark_MDS(Dl2, lands, 2)

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(3, 3), facecolor="white", constrained_layout=True)
    fig.set_size_inches((20, 20))
    plot_2d(ax, xl_2, None, "LMDS")
    plt.show()


if __name__ == '__main__':
    dicker_fisch()
