import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def generate_time_series():
    sampling_rate = 1000  # Number of samples per second
    duration = 20  # Duration of the signal in seconds
    t = np.linspace(0, duration, sampling_rate * duration)
    sine_wave = np.sin(2 * np.pi * t * 0.5)
    return sine_wave

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
    ax.set_title(f"w = {w}", fontsize=30)
    ax.axis("off")

def plot_basic_linechart(data, ax, title):
    ax.plot(data, color="black")
    ax.set_xlim(0, len(data))
    ax.set_title(title, fontsize=30)
    ax.axis("off")

engine1 = np.load("motor-bearing.npy")
engine2 = np.load("motor-run-to-failure.npy")
hydro = np.load("hydro.npy")
harmonic = generate_time_series()

window_steps = [40, 80, 160, 320, 640, 1280, 2560]

fig, ax = plt.subplots(nrows=4, ncols=8)
fig.set_size_inches(70, 30)

plot_basic_linechart(harmonic, ax[0, 0], "Harmonic Oscillation")
plot_basic_linechart(engine1, ax[1, 0], "Engine Vibration")
plot_basic_linechart(engine2, ax[2, 0], "Engine Vibration")
plot_basic_linechart(hydro, ax[3, 0], "Hydro Vibration")

for column in range(len(window_steps)):
    print(f"Window Size {window_steps[column]}")
    plot_tde_projection(harmonic, window_steps[column], ax[0, column + 1], monochrome=True)
    plot_tde_projection(engine1, window_steps[column], ax[1, column + 1])
    plot_tde_projection(engine2, window_steps[column], ax[2, column + 1])
    plot_tde_projection(hydro, window_steps[column], ax[3, column + 1])

plt.savefig("matrix.png", dpi=100, bbox_inches='tight')
