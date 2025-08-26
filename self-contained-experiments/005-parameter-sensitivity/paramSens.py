import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm


def vibration_tde_plot(vibration, w, folder, title):
    plt.clf()
    windows = sliding_window_view(vibration, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    plot_mosaic = [
        ["values", "values", "TDE"]
    ]

    fig, ax = plt.subplot_mosaic(plot_mosaic)
    plt.subplots_adjust(wspace=0.1, hspace=0.3)
    fig.set_size_inches(30, 5)
    ax["values"].plot(vibration, color="black")
    ax["values"].axvspan(0, w, color="red", alpha=0.7)
    ax["values"].set_xlim(0, len(vibration))
    ax["values"].set_title(title, fontsize=30)

    ax["TDE"].scatter(projected[:, 0], projected[:, 1], s=8, c=plt.colormaps["turbo"](scores_norm))
    ax["TDE"].get_xaxis().set_visible(False)
    ax["TDE"].set_title(f"TDE w={w}", fontsize=30)
    plt.savefig(f"{folder}/vibration-tde-{str(w).zfill(4)}.png", bbox_inches='tight', dpi=300)
    plt.close(fig)


vibration = np.load("motor-run-to-failure.npy")
for w in tqdm(range(2, 2500)):
    vibration_tde_plot(vibration, w, "plots-engine-2", "Engine Vibration")

