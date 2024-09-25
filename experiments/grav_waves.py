import os
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from matplotlib import cm

def save_preview_image(data, save_path, marker=None):
    if not marker:
        marker = []
    plt.clf()
    formatter = plticker.FuncFormatter(lambda x_val, tick_pos: f"{x_val}")
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(30, 10)
    ax.plot(np.arange(len(data)), data, color="black")
    ax.set_xlim([0, len(data)])
    ax.xaxis.set_major_formatter(formatter)
    plt.axis('off')
    ax.vlines(marker, ymin=np.min(data), ymax=np.max(data), color="red")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def make_gravitational_waves(
    path_to_data: Path,
    n_signals: int = 30,
    downsample_factor: int = 2,
    r_min: float = 0.075,
    r_max: float = 0.65,
    n_snr_values: int = 10,
        seed: int = None
        ):
    if seed:
        np.random.seed(seed=seed)

    def padrand(V, n, kr):
        cut = np.random.randint(n)
        rand1 = np.random.randn(cut)
        rand2 = np.random.randn(n - cut)
        out = np.concatenate((rand1 * kr, V, rand2 * kr))
        return out

    Rcoef = np.linspace(r_min, r_max, n_snr_values)
    Npad = 500  # number of padding points on either side of the vector
    gw = np.load(path_to_data / "gravitational_wave_signals.npy")
    Norig = len(gw["data"][0])
    Ndat = len(gw["signal_present"])
    N = int(Norig / downsample_factor)

    ncoeff = []
    Rcoeflist = []

    for j in range(n_signals):
        ncoeff.append(10 ** (-19) * (1 / Rcoef[j % n_snr_values]))
        Rcoeflist.append(Rcoef[j % n_snr_values])

    noisy_signals_plain = []
    noisy_signals_anomalous = []
    gw_signals = []

    for j in range(n_signals):
        signal = gw["data"][j % Ndat][range(0, Norig, downsample_factor)]
        noise = ncoeff[j] * np.random.randn(N)
        rawsig_a = padrand(signal + noise, Npad, ncoeff[j])
        rawsig_p = padrand(noise, Npad, ncoeff[j])
        noisy_signals_anomalous.append(rawsig_a.copy())
        noisy_signals_plain.append(rawsig_p.copy())
        gw_signals.append(signal)

    return noisy_signals_plain, noisy_signals_anomalous, gw_signals


def fill_folder(values, signal, base_target_path, name, save_events=True, window_size=500):
    os.mkdir(os.path.join(base_target_path, name))
    np.save(os.path.join(base_target_path, name, "values.npy"), values)
    save_preview_image(signal, os.path.join(base_target_path, name, "signal.png"))
    sig = np.abs(np.diff(signal))
    marker = np.argwhere(sig > np.min(sig) + (np.max(sig) - np.min(sig)) * 0.05).flatten()
    if save_events:
        np.save(os.path.join(base_target_path, name, "events.npy"), [marker[0], marker[-1]])
    save_preview_image(sig, os.path.join(base_target_path, name, "signal2.png"), marker=[marker[0], marker[-1]])
    save_preview_image(values, os.path.join(base_target_path, name, "preview.png"))
    windows = sliding_window_view(values, window_shape=window_size)
    projected = PCA(n_components=2).fit_transform(windows)
    # projected = MinMaxScaler().fit_transform(projected)
    np.save(os.path.join(base_target_path, name, "projected.npy"), projected)


def gen_dataset(n, index=5):
    base_target_path = os.path.join(Path(__file__).parents[1], "data", "samples", "gw")
    if os.path.exists(base_target_path):
        shutil.rmtree(base_target_path)
    if not os.path.exists(base_target_path):
        os.makedirs(base_target_path)

    for i in range(n):
        noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(Path(""), n_signals=10, n_snr_values=10)
        sigp = int((np.random.randn() < 0))
        name = f"abnormal-{i}" if sigp == 1 else f"normal-{i}"
        print(name)
        signal = noisy_signals_anomalous[index] if sigp == 1 else noisy_signals_plain[index]
        signal *= 100_000_000_000
        values = MinMaxScaler().fit_transform(signal.reshape(-1, 1)).reshape(1, -1)[0]
        fill_folder(values, gw_signals[index], base_target_path, name, save_events=sigp == 1)


    # noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(Path(""), n_signals=10, n_snr_values=10)
    # noisy_signals, labels = [], []
    # for i in range(len(noisy_signals_anomalous)):
    #     sigp = int((np.random.randn() < 0))
    #     if sigp == 1:
    #         noisy_signals.append(noisy_signals_anomalous[i])
    #         labels.append(1)
    #     else:
    #         noisy_signals.append(noisy_signals_plain[i])
    #         labels.append(0)
    # count = 0
    # for noisy_signal, signal, label in zip(noisy_signals, gw_signals, labels):
    #     name = f"abnormal-{count}" if int(label) == 1 else f"normal-{count}"
    #     print(name)
    #     os.mkdir(os.path.join(base_target_path, name))
    #     noisy_signal *= 100_000_000_000
    #     print(noisy_signal)
    #     values = MinMaxScaler().fit_transform(noisy_signal.reshape(-1, 1)).reshape(1, -1)[0]
    #     print(values)
    #     fill_folder(values, signal, base_target_path, name, save_events=label == 1)
    #     count += 1

def plot_2d_cloud(values, name):
    plt.clf()
    windows = sliding_window_view(values, window_shape=3000)
    projected = PCA(n_components=2).fit_transform(windows)
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(10, 10)
    ax.set_axis_off()
    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    print(scores)
    colors = cm.get_cmap('turbo')(scores)
    ax.scatter(projected[:, 0], projected[:, 1], s=10, c=colors)
    plt.savefig(name)

def create_vis(index=4):
    noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(Path(""), n_signals=30)

    values_a = noisy_signals_anomalous[index] * 100_000_000_000
    values_a = MinMaxScaler().fit_transform(values_a.reshape(-1, 1)).reshape(1, -1)[0]
    values_p = noisy_signals_plain[index] * 100_000_000_000
    values_p = MinMaxScaler().fit_transform(values_p.reshape(-1, 1)).reshape(1, -1)[0]

    plt.clf()
    fig, ax = plt.subplots(nrows=2, ncols=1)
    fig.set_size_inches(20, 10)
    ax[0].set_xlim([0, len(values_p)])
    ax[0].plot(noisy_signals_plain[index], color="black")
    # ax[1].set_title("Signal with Grav Wave")
    # ax[0].set_title("Raw Signal")
    ax[1].set_xlim([0, len(values_a)])
    ax[1].plot(noisy_signals_anomalous[index], color="black")
    ax[1].plot(gw_signals[index], color="lime", linewidth=3)
    ax[0].axis('off')
    ax[1].axis('off')
    plt.savefig("test.png", bbox_inches='tight')

    plot_2d_cloud(values_a, "test_cloud_a.png")
    plot_2d_cloud(values_p, "test_cloud_p.png")


def hard_dataset(index=4):
    noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(Path(""), n_signals=30)

    values_a = noisy_signals_anomalous[index] * 100_000_000_000
    values_a = MinMaxScaler().fit_transform(values_a.reshape(-1, 1)).reshape(1, -1)[0]
    values_p = noisy_signals_plain[index] * 100_000_000_000
    values_p = MinMaxScaler().fit_transform(values_p.reshape(-1, 1)).reshape(1, -1)[0]

    base_target_path = os.path.join(Path(__file__).parents[1], "data", "samples", "gwhard")
    if os.path.exists(base_target_path):
        shutil.rmtree(base_target_path)
    if not os.path.exists(base_target_path):
        os.makedirs(base_target_path)

    fill_folder(values_p, gw_signals[index], base_target_path, "normal", save_events=False, window_size=3000)
    fill_folder(values_a, gw_signals[index], base_target_path, "abnormal", save_events=True, window_size=3000)


if __name__ == '__main__':
    gen_dataset(20)
    # create_vis(index=24)
    # hard_dataset(index=24)