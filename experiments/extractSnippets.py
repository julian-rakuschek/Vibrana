import os
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA


def save_preview_image(data, save_path):
    plt.clf()
    formatter = plticker.FuncFormatter(lambda x_val, tick_pos: f"{x_val}")
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(30, 10)
    ax.plot(np.arange(len(data)), data, color="black")
    ax.set_xlim([0, len(data)])
    ax.xaxis.set_major_formatter(formatter)
    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


folder = "5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt"
base_path = os.path.join(Path(__file__).parents[1], "data", folder)
folder_values = np.load(os.path.join(base_path, "values.npy"))
folder_values = folder_values[80_000:950_000]

if os.path.exists("snippets"):
    shutil.rmtree("snippets")
os.mkdir("snippets")

window_size = 100_000
needle = 0
while needle < len(folder_values):
    name = str(needle // window_size).zfill(4)
    print(name)
    extracted = folder_values[needle:needle+window_size]
    os.mkdir(os.path.join("snippets", name))
    np.save(os.path.join("snippets", name, "values.npy"), extracted)
    save_preview_image(extracted, os.path.join("snippets", name, "preview.png"))
    windows = sliding_window_view(extracted, window_shape=2000)
    projected = PCA(n_components=2).fit_transform(windows)
    np.save(os.path.join("snippets", name, "projected.npy"), projected)
    needle += window_size
