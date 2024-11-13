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


def make_gravitational_waves(
    n_signals: int = 30,
    downsample_factor: int = 2,
    snr: float = 0.075,
        seed: int = None
        ):
    if seed:
        np.random.seed(seed=seed)

    def padrand(V, Npad, coeff):
        cut = np.random.randint(Npad)
        rand1 = np.random.randn(cut)
        rand2 = np.random.randn(Npad - cut)
        out = np.concatenate((rand1 * coeff, V, rand2 * coeff))
        return out, cut

    Npad = 4_000  # number of padding points on either side of the vector
    file_path = os.path.join(Path(__file__).parents[1], "data", "raw", "grav", "gravitational_wave_signals.npy")
    gw = np.load(file_path)
    Norig = len(gw["data"][0])
    Ndat = len(gw["signal_present"])
    N = int(Norig / downsample_factor)

    coeff = 10 ** (-19) * (1 /snr)

    noisy_signals_plain = []
    noisy_signals_anomalous = []
    gw_signals = []

    for j in range(n_signals):
        signal = gw["data"][j % Ndat][range(0, Norig, downsample_factor)]
        noise = coeff * np.random.randn(N)
        rawsig_a, cut = padrand(signal + noise, Npad, coeff)
        print(cut)
        rawsig_p, _ = padrand(noise, Npad, coeff)
        noisy_signals_anomalous.append(rawsig_a.copy())
        noisy_signals_plain.append(rawsig_p.copy())
        gw_signals.append(np.concatenate((np.repeat(0, cut), signal, np.repeat(0, Npad - cut))))

    return noisy_signals_plain, noisy_signals_anomalous, gw_signals


def gen_dataset(n=20, snr=0.15):
    base_target_path = os.path.join(Path(__file__).parents[1], "data", "parsed", "grav", f"grav-{str(snr).replace('.', '')}")
    Path(base_target_path).mkdir(parents=True, exist_ok=True)
    for i in range(n):
        noisy_signals_plain, noisy_signals_anomalous, gw_signals = make_gravitational_waves(n_signals=30, snr=snr)

        # This Multiplication with 100_000_000_000 is necessary since the values are so small
        # that MinMaxScaler is not working due to numerical imprecision.
        values_a = noisy_signals_anomalous[0] * (10 ** 19)
        values_a = MinMaxScaler().fit_transform(values_a.reshape(-1, 1)).reshape(1, -1)[0]
        values_p = noisy_signals_plain[0] * (10 ** 19)
        values_p = MinMaxScaler().fit_transform(values_p.reshape(-1, 1)).reshape(1, -1)[0]

        np.save(os.path.join(base_target_path, f"values-anomalous-{str(i).zfill(3)}.npy"), values_a)
        np.save(os.path.join(base_target_path, f"values-normal-{str(i).zfill(3)}.npy"), values_p)


if __name__ == '__main__':
    gen_dataset(n=20, snr=0.1)
    gen_dataset(n=20, snr=0.15)
    gen_dataset(n=20, snr=0.2)
    # create_vis(index=24)
    # hard_dataset(index=24)
