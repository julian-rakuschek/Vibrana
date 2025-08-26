import random

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import ShortTimeFFT
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from parser.grav_waves import make_gravitational_waves


def vis_problem():
    plt.clf()

    noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(1, snr=0.1)

    fig, ax = plt.subplots(nrows=2, ncols=1)
    fig.set_size_inches(20, 10)
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    ax[0].plot(noisy_signals_plain[0], color="black")
    ax[0].set_xlim(0, len(noisy_signals_plain[0]))
    ax[0].set_axis_off()

    ax[1].plot(noisy_signals_anomalous[0], color="black")
    ax[1].set_xlim(0, len(noisy_signals_anomalous[0]))
    ax[1].set_axis_off()
    plt.savefig(f"problem.png", bbox_inches='tight', dpi=200)
    ax[1].plot(gw_signals[0], color="green")

    plt.savefig(f"problem_with_secret.png", bbox_inches='tight', dpi=200)


def vis_problem_with_spectro():
    plt.clf()

    noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(1, snr=0.2)

    fig, ax = plt.subplots(nrows=2, ncols=2)
    fig.set_size_inches(30, 10)
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    ax[0, 0].plot(noisy_signals_plain[0], color="black")
    ax[0, 0].set_xlim(0, len(noisy_signals_plain[0]))
    ax[0, 0].set_axis_off()

    ax[1, 0].plot(noisy_signals_anomalous[0], color="black")
    ax[1, 0].set_xlim(0, len(noisy_signals_anomalous[0]))
    ax[1, 0].set_axis_off()
    ax[1, 0].plot(gw_signals[0], color="green")

    w = np.repeat(1, 2000)
    SFT = ShortTimeFFT(w, hop=1, fs=2_000, mfft=None, scale_to="magnitude")
    Sx = SFT.spectrogram(noisy_signals_plain[0])
    Sx[Sx > np.percentile(Sx, 95)] = np.percentile(Sx, 95)
    ax[0, 1].imshow(Sx, origin='lower', aspect='auto', extent=SFT.extent(len(noisy_signals_plain[0])), cmap='viridis')
    ax[0, 1].get_xaxis().set_visible(False)

    w = np.repeat(1, 2000)
    SFT = ShortTimeFFT(w, hop=1, fs=2_000, mfft=None, scale_to="magnitude")
    Sx = SFT.spectrogram(noisy_signals_anomalous[0])
    Sx[Sx > np.percentile(Sx, 95)] = np.percentile(Sx, 95)
    ax[1, 1].imshow(Sx, origin='lower', aspect='auto', extent=SFT.extent(len(noisy_signals_anomalous[0])), cmap='viridis')
    ax[1, 1].get_xaxis().set_visible(False)

    plt.savefig(f"problem_with_spectro.png", bbox_inches='tight', dpi=200)


def grav_waves_spectrograms_tdes():
    noisy_signals_plain, noisy_signals_anomalous = [], []
    for _ in range(25):
        noisy, anomalous, gw_signals = make_gravitational_waves(1, snr=0.2)
        noisy_signals_plain.append(noisy[0])
        noisy_signals_anomalous.append(anomalous[0])
    combined = noisy_signals_plain + noisy_signals_anomalous
    np.random.shuffle(combined)

    fig, ax = plt.subplots(nrows=5, ncols=5)
    fig.set_size_inches(20, 15)
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    count = 0
    for i in range(5):
        for j in range(5):
            print(i, j)
            w = np.repeat(1, 2000)
            SFT = ShortTimeFFT(w, hop=1, fs=2_000, mfft=None, scale_to="magnitude")
            Sx = SFT.spectrogram(combined[count])
            Sx[Sx > np.percentile(Sx, 95)] = np.percentile(Sx, 95)
            ax[i, j].imshow(Sx, origin='lower', aspect='auto', extent=SFT.extent(len(combined[count])), cmap='viridis')
            ax[i, j].get_xaxis().set_visible(False)
            count += 1
    plt.savefig(f"spectro_grid.png", bbox_inches='tight', dpi=100)

    plt.clf()
    fig, ax = plt.subplots(nrows=5, ncols=5)
    fig.set_size_inches(20, 15)
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    count = 0
    for i in range(5):
        for j in range(5):
            windows = sliding_window_view(combined[count], window_shape=2_000)
            windows = StandardScaler().fit_transform(windows)
            projected = PCA(n_components=2).fit_transform(windows)

            scores_2d = [np.linalg.norm(point) for point in projected]
            scores_2d_norm = MinMaxScaler().fit_transform(np.array(scores_2d).reshape(-1, 1))[:, 0]

            ax[i, j].scatter(projected[:, 0], projected[:, 1], s=8, c=colormaps["turbo"](scores_2d_norm))
            ax[i, j].axis("off")

            count += 1
    plt.savefig(f"tde_grid.png", bbox_inches='tight', dpi=100)



if __name__ == '__main__':
    grav_waves_spectrograms_tdes()
