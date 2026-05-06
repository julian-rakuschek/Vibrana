import json
from pathlib import Path

import numpy as np
from dataclasses import dataclass
import shutil
import os

@dataclass
class SegmentType:
    name: str
    kind: str  # "sine", "multi_sine", "chirp", "noise"
    freqs: tuple = ()
    amp: float = 1.0
    noise_std: float = 0.1


segment_types = [
    SegmentType("A", "sine", freqs=(30,), amp=1.0, noise_std=0.10),
    SegmentType("B", "sine", freqs=(75,), amp=0.8, noise_std=0.15),
    SegmentType("C", "multi_sine", freqs=(40, 120), amp=1.0, noise_std=0.10),
    SegmentType("D", "multi_sine", freqs=(90, 180), amp=0.7, noise_std=0.20),
    SegmentType("E", "chirp", freqs=(20, 120), amp=0.9, noise_std=0.10),
    SegmentType("F", "chirp", freqs=(150, 40), amp=0.9, noise_std=0.15),
    SegmentType("G", "noise", amp=0.0, noise_std=0.8),
    SegmentType("H", "sine", freqs=(220,), amp=0.5, noise_std=0.25),
    SegmentType("I", "multi_sine", freqs=(15, 55, 95), amp=1.1, noise_std=0.12),
    SegmentType("J", "noise", amp=0.0, noise_std=0.3),
]

import matplotlib.pyplot as plt
import numpy as np


def plot_segment_stripe(boundaries, path, fs=1.0, figsize=(20, 2), ):
    labels_unique = sorted(set(label for _, _, label in boundaries))
    cmap = plt.get_cmap("tab10", len(labels_unique))
    label_to_color = {lab: cmap(i) for i, lab in enumerate(labels_unique)}
    fig, ax = plt.subplots(figsize=figsize)
    for start, end, label in boundaries:
        start_t = start / fs
        width = (end - start) / fs
        ax.barh(y=0, width=width, left=start_t, height=1, align="edge", color=label_to_color[label], edgecolor="black")
    ax.set_yticks([])
    ax.set_xlabel("Time [s]")
    ax.set_title("Segment Structure")
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=label_to_color[l])
        for l in labels_unique
    ]
    ax.legend(handles, labels_unique, bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(path)


def make_segment(seg_type, n, fs, rng):
    t = np.arange(n) / fs

    if seg_type.kind == "sine":
        phase = rng.uniform(0, 2 * np.pi)
        x = seg_type.amp * np.sin(2 * np.pi * seg_type.freqs[0] * t + phase)

    elif seg_type.kind == "multi_sine":
        x = np.zeros(n)
        for f in seg_type.freqs:
            phase = rng.uniform(0, 2 * np.pi)
            x += np.sin(2 * np.pi * f * t + phase)
        x *= seg_type.amp / max(len(seg_type.freqs), 1)

    elif seg_type.kind == "chirp":
        f0, f1 = seg_type.freqs
        k = (f1 - f0) / max(t[-1], 1 / fs)
        phase = 2 * np.pi * (f0 * t + 0.5 * k * t ** 2)
        x = seg_type.amp * np.sin(phase)

    elif seg_type.kind == "noise":
        x = np.zeros(n)

    else:
        raise ValueError(f"Unknown segment kind: {seg_type.kind}")

    x += rng.normal(0, seg_type.noise_std, size=n)
    return x


def generate_vibration_signal(
        fs=1000,
        total_samples=20000,
        min_len=100,
        max_len=3000,
        p_repeat=0.65,
        seed=0,
):
    rng = np.random.default_rng(seed)
    signal = []
    # labels = []
    boundaries = []

    current_type = rng.integers(len(segment_types))
    pos = 0

    while pos < total_samples:
        if rng.random() > p_repeat:
            current_type = rng.integers(len(segment_types))

        seg_len = rng.integers(min_len, max_len + 1)
        seg_len = min(seg_len, total_samples - pos)

        seg_type = segment_types[current_type]
        x_seg = make_segment(seg_type, seg_len, fs, rng)

        signal.append(x_seg)
        # labels.extend([seg_type.name] * seg_len)
        boundaries.append((pos, pos + seg_len, seg_type.name))

        pos += seg_len

    return np.concatenate(signal), boundaries


def save_signal(signal, boundaries):
    distinct_segments = len(list(set([b[2] for b in boundaries])))
    dataset_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "synthetic")
    subset_folder = os.path.join(dataset_folder, f"Experiment 1 ({distinct_segments} segments)")
    os.makedirs(subset_folder, exist_ok=True)

    meta = {
        "name": "Synthethic Signals",
        "description": "Artificial signals generated to demonstrate clustering with many diverse segment types.",
        "task": "Changepoint Detection",
        "loader": "disk"
    }
    with open(os.path.join(dataset_folder, "meta.json"), "w") as f:
        f.write(json.dumps(meta, indent=4))

    time_json = {
      "start_time": "2022-01-01T00:00:00+00:00",
      "end_time": "2022-01-01T23:59:00+00:00",
      "total_sample_points": len(signal),
      "display_as_delta": False
    }
    with open(os.path.join(subset_folder, "time.json"), "w") as f:
        f.write(json.dumps(time_json, indent=4))
    np.save(os.path.join(subset_folder, "values.npy"), signal)
    plot_segment_stripe(boundaries, os.path.join(subset_folder, "stripe.png"))


if __name__ == '__main__':
    signal, boundaries = generate_vibration_signal(
        total_samples=100_000_000,
        min_len=20_000,
        max_len=500_000,
    )
    save_signal(signal, boundaries)
