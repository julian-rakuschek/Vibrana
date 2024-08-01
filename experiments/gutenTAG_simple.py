import json
import random

import numpy as np
from gutenTAG import GutenTAG
from matplotlib import pyplot as plt
from sklearn.metrics import f1_score, accuracy_score
from tqdm import tqdm

from algorithms.damp_hpi import DAMP


def get_base_ts(name="dirichlet-sine"):
    frequency = 1000
    # variance = np.random.normal(loc=0.1, scale=0.02)
    variance = 0.1
    amplitude = 0.5
    return {
        "name": "test",
        "length": 1000,
        "base-oscillations": [
            {
                "kind": "dirichlet",
                "frequency": frequency,
                "variance": variance,
                "amplitude": amplitude,
            },
        ],
        "semi-supervised": True,
        "supervised": False,
        "anomalies": []
    }


def get_mean_anomaly(base_config, pos="middle"):
    length = int(np.random.normal(loc=150, scale=50))
    offset = np.random.normal(loc=0, scale=2)
    print(pos, length, offset)
    base_config["anomalies"].append(
        {"length": length, "channel": 0, "position": pos, "kinds": [
            {"kind": "mean", "offset": offset},
        ]})
    return base_config


def get_amplitude_anomaly(base_config, pos="middle"):
    amplitude_factor = np.random.normal(loc=3, scale=0.5)
    length = random.choice([i for i in range(100, 200, 20)])
    print(pos, length, amplitude_factor)
    base_config["anomalies"].append(
        {"length": length, "channel": 0, "position": pos, "kinds": [
            {"kind": "amplitude", "amplitude_factor": amplitude_factor},
        ]})
    return base_config


def get_extremum_anomaly(base_config, pos="middle"):
    base_config["anomalies"].append(
        {"length": 1, "channel": 0, "position": pos, "kinds": [
            {"kind": "extremum", "min": random.choice([True, False]), "local": random.choice([True, False])},
        ]})
    return base_config


def get_frequency_anomaly(base_config, pos="middle"):
    length = random.choice([i for i in range(30, 200, 10)])
    frequency_factor = np.random.normal(loc=0, scale=5)
    print(pos, length, frequency_factor)
    base_config["anomalies"].append(
        {"length": length, "channel": 0, "position": pos, "kinds": [
            {"kind": "frequency", "frequency_factor": frequency_factor},
        ]})
    return base_config


def get_pattern_shift_anomaly(base_config, pos="middle"):
    length = 200
    shift_by = 150
    transition_window = shift_by
    print(pos, length, shift_by, transition_window)
    base_config["anomalies"].append(
        {"length": length, "channel": 0, "position": pos, "kinds": [
            {"kind": "pattern-shift", "shift_by": shift_by, "transition_window": transition_window},
        ]})
    return base_config


def get_platform_anomaly(base_config, pos="middle"):
    length = random.choice([i for i in range(10, 150, 10)])
    value = np.random.normal(loc=0, scale=0.3)
    print(pos, length, value)
    base_config["anomalies"].append(
        {"length": length, "channel": 0, "position": pos, "kinds": [
            {"kind": "platform", "value": value},
        ]})
    return base_config


def get_variance_anomaly(base_config, pos="middle"):
    length = random.choice([i for i in range(10, 150, 10)])
    value = max(np.random.normal(loc=0.2, scale=0.02), 0.05)
    print(pos, length, value)
    base_config["anomalies"].append(
        {"length": length, "channel": 0, "position": pos, "kinds": [
            {"kind": "variance", "variance": value},
        ]})
    return base_config


mapping = {
    "mean": get_mean_anomaly,
    "variance": get_variance_anomaly,
    "amplitude": get_amplitude_anomaly,
    "extremum": get_extremum_anomaly,
    "platform": get_platform_anomaly,
    "frequency": get_frequency_anomaly
}


def example_ts_as_csv(name, anomaly_func_1=None, anomaly_func_2=None, anomaly_func_3=None):
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    anomaly_funcs = [anomaly_func_1, anomaly_func_2, anomaly_func_3]
    for anomaly_func in anomaly_funcs:
        if anomaly_func is not None:
            ts = anomaly_func(ts, pos="beginning")
            ts = anomaly_func(ts, pos="middle")
            ts = anomaly_func(ts, pos="end")
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    df = datasets[0].timeseries
    df.drop(columns=["is_anomaly"], inplace=True)
    df.to_csv(f"{name}.csv", index=False)
    return df


def get_random_anomaly_ts(name, anomaly_funcs, anomaly_free=False, pos=None):
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    positions = ["beginning", "middle", "end"]
    if not anomaly_free:
        ts = random.choice(anomaly_funcs)(ts, pos=random.choice(positions) if pos is None else pos)
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    df = datasets[0].timeseries
    return df




def generate_example_csv():
    example_ts_as_csv("anomaly-free")
    example_ts_as_csv("mean", anomaly_func_1=get_mean_anomaly)
    example_ts_as_csv("amplitude", anomaly_func_1=get_amplitude_anomaly)
    example_ts_as_csv("extremum", anomaly_func_1=get_extremum_anomaly)
    example_ts_as_csv("frequency", anomaly_func_1=get_frequency_anomaly)
    example_ts_as_csv("shift", anomaly_func_1=get_pattern_shift_anomaly)
    example_ts_as_csv("platform", anomaly_func_1=get_platform_anomaly)
    example_ts_as_csv("variance", anomaly_func_1=get_variance_anomaly)


def plot_anomaly(name):
    ts = get_random_anomaly_ts(name, [mapping[name]], pos="middle")
    print(ts)
    mask_anomaly = ts.to_numpy()[:, 1] == 1
    mask_segment_idx_first = np.argmax(ts.to_numpy()[:, 1])
    mask_segment_idx_last = len(ts.to_numpy()[:, 1][::-1]) - np.argmax(ts.to_numpy()[:, 1][::-1]) - 1

    mask_anomaly[mask_segment_idx_first - 1] = 1
    mask_anomaly[mask_segment_idx_last + 1] = 1
    x = np.arange(len(mask_anomaly))
    mask_segment_1 = [i < mask_segment_idx_first for i in x]
    mask_segment_2 = [i > mask_segment_idx_last for i in x]

    plt.figure(figsize=(15, 6))
    plt.plot(x[mask_segment_1], ts.to_numpy()[:, 0][mask_segment_1], color="black")
    plt.plot(x[mask_anomaly], ts.to_numpy()[:, 0][mask_anomaly], color="red")
    plt.plot(x[mask_segment_2], ts.to_numpy()[:, 0][mask_segment_2], color="black")
    plt.title(f"{name.capitalize()} Anomaly")
    plt.savefig(f"{name}.png", bbox_inches='tight', dpi=200)


def damp_test():
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    ts = get_frequency_anomaly(ts, pos="middle")
    # ts = get_amplitude_anomaly(ts, pos="end")
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    df = datasets[0].timeseries
    df.drop(columns=["is_anomaly"], inplace=True)
    values = df.to_numpy()[:, 0]
    fig, ax = plt.subplots(nrows=2, ncols=1)
    ax[0].plot(values)
    damp = DAMP()
    res = damp.fit_transform(values)
    print(res)
    ax[1].plot(res)
    plt.show()


if __name__ == '__main__':
    # plot_anomaly("variance")
    # pump_into_anoscout("Simple", 100)
    # assess_accuracy("GutenTAG")
    damp_test()
