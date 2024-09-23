import os
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

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
        ):
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

    noisy_signals = []
    gw_signals = []
    k = 0
    labels = np.zeros(n_signals)

    for j in range(n_signals):
        signal = gw["data"][j % Ndat][range(0, Norig, downsample_factor)]
        sigp = int((np.random.randn() < 0))
        noise = ncoeff[j] * np.random.randn(N)
        labels[j] = sigp
        if sigp == 1:
            rawsig = padrand(signal + noise, Npad, ncoeff[j])
            if k == 0:
                k = 1
        else:
            rawsig = padrand(noise, Npad, ncoeff[j])
        noisy_signals.append(rawsig.copy())
        gw_signals.append(signal)

    return noisy_signals, gw_signals, labels


def gen_dataset():
    base_target_path = os.path.join(Path(__file__).parents[1], "data", "samples", "gw")
    if os.path.exists(base_target_path):
        shutil.rmtree(base_target_path)
    if not os.path.exists(base_target_path):
        os.makedirs(base_target_path)

    noisy_signals, gw_signals, labels = make_gravitational_waves(Path(""), n_signals=10, n_snr_values=10)
    count = 0
    for noisy_signal, signal, label in zip(noisy_signals, gw_signals, labels):
        name = f"abnormal-{count}" if int(label) == 1 else f"normal-{count}"
        print(name)
        os.mkdir(os.path.join(base_target_path, name))
        noisy_signal *= 100_000_000_000
        print(noisy_signal)
        values = MinMaxScaler().fit_transform(noisy_signal.reshape(-1, 1)).reshape(1, -1)[0]
        print(values)
        np.save(os.path.join(base_target_path, name, "values.npy"), values)
        save_preview_image(signal, os.path.join(base_target_path, name, "signal.png"))

        sig = np.abs(np.diff(signal))
        marker = np.argwhere(sig > np.min(sig) + (np.max(sig) - np.min(sig)) * 0.05).flatten()
        if label == 1:
            np.save(os.path.join(base_target_path, name, "events.npy"), [marker[0], marker[-1]])
        save_preview_image(sig, os.path.join(base_target_path, name, "signal2.png"), marker=[marker[0], marker[-1]])
        save_preview_image(values, os.path.join(base_target_path, name, "preview.png"))
        windows = sliding_window_view(values, window_shape=500)
        projected = PCA(n_components=2).fit_transform(windows)
        # projected = MinMaxScaler().fit_transform(projected)
        np.save(os.path.join(base_target_path, name, "projected.npy"), projected)
        count += 1


if __name__ == '__main__':
    gen_dataset()