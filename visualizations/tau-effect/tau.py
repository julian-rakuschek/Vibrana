import itertools

import numpy as np
from matplotlib.pyplot import colormaps
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA


def time_delay_embedding(values, d, tau=1, stride=1):
    values = np.asarray(values)
    windows = []
    index = 0
    while index <= len(values) - d:
        window = []
        for i in range(index, index + d * tau, tau):
            if i >= len(values):
                return np.array(windows)
            window.append(values[i])
        windows.append(window)
        index += stride
    return np.array(windows)


def plot_embedding(ax, tde, title="TDE"):
    projected = PCA(n_components=2).fit_transform(tde)
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores = np.array(scores)
    scores_norm = (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
    ax.scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps["turbo"](scores_norm))
    ax.axis("off")
    ax.set_title(title, fontsize=30)


def tau_vis():
    values = np.load("values.npy")
    print(len(values))
    exit()
    tau_values = [1, 50, 80, 95, 100]
    stride_values = [1, 10, 100, 1000]
    for t, s in itertools.product(tau_values, stride_values):
        print(s, t)
        plt.clf()
        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(10, 10)
        tde = time_delay_embedding(values, d=1000, tau=t, stride=s)
        plot_embedding(ax, tde, title=f"TDE with tau={t} and s={s}")
        plt.savefig(f"plots/tde_t{t}_s{s}.png",  bbox_inches='tight', dpi=100)


def dummy():
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    tde = time_delay_embedding(a, 3, 2, 2)
    print(tde)


if __name__ == '__main__':
    tau_vis()
