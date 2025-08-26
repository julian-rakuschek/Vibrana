import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def plot_tde_projection(data, w, ax, monochrome=False):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)

    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    ax.scatter(projected[:, 0], projected[:, 1], s=8, c="black" if monochrome else plt.colormaps["turbo"](scores_norm))
    # ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")


def vis_problem():
    np.random.seed(seed=42)
    n = 10_000
    noise = 6 * np.random.randn(n)
    t = np.linspace(0, 1, n)
    sine_wave = np.sin(2 * np.pi * 30 * t)
    noise_with_signal = sine_wave + noise

    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(30, 10)
    ax.plot(noise, color="black")
    ax.set_xlim(0, len(noise))
    ax.set_axis_off()
    plt.savefig(f"noise_line.png", dpi=300, transparent=True)

    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(30, 10)
    ax.plot(noise_with_signal, color="black")
    ax.set_xlim(0, len(noise_with_signal))
    ax.set_axis_off()
    plt.savefig(f"secret.png", dpi=300, transparent=True)
    ax.plot(sine_wave, color="#304ffe", linewidth=5)
    plt.savefig(f"secret_line.png", dpi=300, transparent=True)

    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    plot_tde_projection(noise, 1000, ax)
    plt.savefig(f"TDE_noise.png", dpi=300, transparent=True)

    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    plot_tde_projection(noise_with_signal, 1000, ax)
    plt.savefig(f"TDE_anomaly.png", dpi=300, transparent=True)


if __name__ == '__main__':
    vis_problem()
