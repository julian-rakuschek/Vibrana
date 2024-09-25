import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from gutenTAG import GutenTAG
from mpl_toolkits.axisartist import SubplotZero

def get_base_ts(name="dirichlet-sine", frequency=400, amplitude=0.5, length=1000):
    variance = 0.1
    return {
        "name": "test",
        "length": length,
        "base-oscillations": [
            {
                "kind": "sine",
                "frequency": frequency,
                "variance": variance,
                "amplitude": amplitude,
            },
        ],
        "semi-supervised": True,
        "supervised": False,
        "anomalies": []
    }

def plot_clustering():
    window_size = 201
    x = np.linspace(-np.pi, np.pi, window_size)
    sin_pattern_high = np.sin(3*x)
    sin_pattern_low = np.sin(x)
    patterns = [sin_pattern_high, sin_pattern_low]
    pattern_colors = ["pink", "lime"]
    pattern_order = [0,1,0,1,0]
    a = np.array([patterns[p] for p in pattern_order])
    a = a.reshape(-1)

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    ax.plot(a, c="w", linewidth=5)
    plt.savefig("clustering_raw.png", bbox_inches='tight', transparent=True, dpi=300)

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    ax.plot(a, c="w", linewidth=5)
    for i, p in enumerate(pattern_order):
        ax.axvline(i*window_size, color="pink", linewidth=8)
    plt.savefig("clustering_segments.png", bbox_inches='tight', transparent=True, dpi=300)

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    ax.plot(a, c="w", linewidth=5)
    for i, p in enumerate(pattern_order):
        ax.axvspan(i*window_size, (i+1)*window_size, color=pattern_colors[p], alpha=0.25)
    plt.savefig("clustering_complete.png", bbox_inches='tight', transparent=True, dpi=300)


def plot_search():
    window_size = 201
    x = np.linspace(-np.pi, np.pi, window_size)
    sin_pattern_high = np.sin(3*x)
    sin_pattern_low = np.sin(x)
    patterns = [sin_pattern_high, sin_pattern_low]
    pattern_colors = ["#340B50", "lime"]
    pattern_order = [0,1,0,1,0]
    pattern_query = 1
    a = np.array([patterns[p] for p in pattern_order])
    a = a.reshape(-1)

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    ax.plot(a, c="w", linewidth=5)
    plt.savefig("search_raw.png", bbox_inches='tight', transparent=True, dpi=300)

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_axis_off()
    ax.plot(patterns[pattern_query], c="w", linewidth=5)
    plt.savefig("search_query.png", bbox_inches='tight', transparent=True, dpi=300)

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    ax.plot(a, c="w", linewidth=5)
    for i, p in enumerate(pattern_order):
        if p == pattern_query:
            ax.axvspan(i*window_size, (i+1)*window_size, color="lime", alpha=0.25)
    plt.savefig("search_complete.png", bbox_inches='tight', transparent=True, dpi=300)

def plot_anomaly_clear():
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    df = datasets[0].timeseries
    values = df.to_numpy()[:, 0]

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    ax.plot(values, color="white", linewidth=3)
    plt.savefig('anomaly_clear.png', dpi=300, transparent=True, bbox_inches='tight')


def plot_anomaly_extremum():
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    ts = datasets[0].timeseries
    values = ts.to_numpy()[:, 0]
    values[200] = -1.3
    values[750] = 0.7
    mask_anomaly = np.zeros(len(values))
    mask_anomaly[195:205] = 1
    mask_anomaly[745:755] = 1
    x = np.arange(len(mask_anomaly))

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    plt.plot(x[0:195], values[0:195], color="white", linewidth=3)
    plt.plot(x[195:205], values[195:205], color="#ffa600", linewidth=3)
    plt.plot(x[205:745], values[205:745], color="white", linewidth=3)
    plt.plot(x[745:755], values[745:755], color="#ffa600", linewidth=3)
    plt.plot(x[755:999], values[755:999], color="white", linewidth=3)
    plt.savefig('anomaly_extremum.png', dpi=300, bbox_inches='tight', transparent=True)


def plot_anomaly_frequency():
    def get_frequency_anomaly(base_config, pos="middle", length=200, frequency_factor=0.5):
        length = 200
        frequency_factor = 0.5
        print(pos, length, frequency_factor)
        base_config["anomalies"].append(
            {"length": length, "channel": 0, "position": pos, "kinds": [
                {"kind": "frequency", "frequency_factor": frequency_factor},
            ]})
        return base_config

    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    ts = get_frequency_anomaly(ts, pos="middle")
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    ts = datasets[0].timeseries
    mask_anomaly = ts.to_numpy()[:, 1] == 1
    mask_segment_idx_first = np.argmax(ts.to_numpy()[:, 1])
    mask_segment_idx_last = len(ts.to_numpy()[:, 1][::-1]) - np.argmax(ts.to_numpy()[:, 1][::-1]) - 1

    mask_anomaly[mask_segment_idx_first - 1] = 1
    mask_anomaly[mask_segment_idx_last + 1] = 1
    x = np.arange(len(mask_anomaly))
    mask_segment_1 = [i < mask_segment_idx_first for i in x]
    mask_segment_2 = [i > mask_segment_idx_last for i in x]

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    plt.plot(x[mask_segment_1], ts.to_numpy()[:, 0][mask_segment_1], color="white", linewidth=3)
    plt.plot(x[mask_anomaly], ts.to_numpy()[:, 0][mask_anomaly], color="#ffa600", linewidth=3)
    plt.plot(x[mask_segment_2], ts.to_numpy()[:, 0][mask_segment_2], color="white", linewidth=3)
    plt.savefig('anomaly_frequency.png', dpi=300, bbox_inches='tight', transparent=3)

def plot_anomaly_trend():
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    ts = datasets[0].timeseries
    values = ts.to_numpy()[:, 0]
    values = np.array([v if idx < 500 else v + (idx - 500) * 0.004 for idx, v in enumerate(values)])
    x = np.arange(len(ts.to_numpy()[:, 0]))
    mask_segment_1 = [i < 500 for i in x]
    mask_segment_2 = [i >= 500 for i in x]

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    plt.plot(x[mask_segment_1], values[mask_segment_1], color="white", linewidth=3)
    plt.plot(x[mask_segment_2], values[mask_segment_2], color="#ffa600", linewidth=3)
    plt.savefig('anomaly_trend.png', dpi=300, bbox_inches='tight', transparent=True)

def plot_prediction():
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    ts = datasets[0].timeseries
    values = ts.to_numpy()[:, 0]
    x = np.arange(len(ts.to_numpy()[:, 0]))
    mask_segment_1 = [i < 700 for i in x]
    mask_segment_2 = [i >= 700 for i in x]

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    plt.plot(x[mask_segment_1], values[mask_segment_1], color="white", linewidth=3)
    plt.plot(x[mask_segment_2], values[mask_segment_2], color="orange", linewidth=3, alpha=0)
    plt.savefig('prediction_todo.png', dpi=300, bbox_inches='tight', transparent=True)

    plt.clf()
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.set_axis_off()
    plt.plot(x[mask_segment_1], values[mask_segment_1], color="white", linewidth=3)
    plt.plot(x[mask_segment_2], values[mask_segment_2], color="orange", linewidth=3)
    plt.savefig('prediction_done.png', dpi=300, bbox_inches='tight', transparent=True)


if __name__ == '__main__':
    plot_clustering()
