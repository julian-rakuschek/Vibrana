import json
from pathlib import Path

import humanize
import numpy as np
from dataclasses import dataclass
import os
from numpy.lib.format import open_memmap
from tqdm import tqdm

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


def plot_segment_stripe(boundaries, path, fs=1.0, figsize=(100, 2), ):
    labels_unique = sorted(set(label for _, _, label in boundaries))
    cmap = plt.get_cmap("tab10", len(labels_unique))
    label_to_color = {lab: cmap(i) for i, lab in enumerate(labels_unique)}
    fig, ax = plt.subplots(figsize=figsize)
    for start, end, label in boundaries:
        start_t = start / fs
        width = (end - start) / fs
        ax.barh(y=0, width=width, left=start_t, height=1, align="edge", color=label_to_color[label])
    min_start = min(start for start, _, _ in boundaries) / fs
    max_end = max(end for _, end, _ in boundaries) / fs
    ax.set_xlim(min_start, max_end)
    ax.margins(x=0)
    ax.set_yticks([])
    ax.set_xlabel("Time [s]")
    ax.set_title("Segment Structure")
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=label_to_color[l])
        for l in labels_unique
    ]
    ax.legend(
        handles,
        labels_unique,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.35),
        ncol=min(len(labels_unique), 10),
    )
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close(fig)


@dataclass
class SegmentState:
    type: SegmentType
    length: int
    phases: tuple = ()


def create_segment_state(seg_type, length, rng):
    if seg_type.kind == "sine":
        phases = (rng.uniform(0, 2 * np.pi),)
    elif seg_type.kind == "multi_sine":
        phases = tuple(rng.uniform(0, 2 * np.pi) for _ in seg_type.freqs)
    else:
        phases = ()
    return SegmentState(seg_type, int(length), phases)


def make_segment_chunk(segment, start_offset, n, fs, rng, dtype=np.float32):
    seg_type = segment.type
    t = (start_offset + np.arange(n)) / fs

    if seg_type.kind == "sine":
        phase = segment.phases[0]
        x = seg_type.amp * np.sin(2 * np.pi * seg_type.freqs[0] * t + phase)

    elif seg_type.kind == "multi_sine":
        x = np.zeros(n)
        for f, phase in zip(seg_type.freqs, segment.phases):
            x += np.sin(2 * np.pi * f * t + phase)
        x *= seg_type.amp / max(len(seg_type.freqs), 1)

    elif seg_type.kind == "chirp":
        f0, f1 = seg_type.freqs
        segment_duration = max((segment.length - 1) / fs, 1 / fs)
        k = (f1 - f0) / segment_duration
        phase = 2 * np.pi * (f0 * t + 0.5 * k * t ** 2)
        x = seg_type.amp * np.sin(phase)

    elif seg_type.kind == "noise":
        x = np.zeros(n)

    else:
        raise ValueError(f"Unknown segment kind: {seg_type.kind}")

    x += rng.normal(0, seg_type.noise_std, size=n)
    return x.astype(dtype, copy=False)


def generate_vibration_signal(
        fs=1000,
        total_samples=20000,
        min_len=100,
        max_len=3000,
        p_repeat=0.65,
        seed=0,
        dtype=np.float32,
        show_progress=True,
):
    rng = np.random.default_rng()
    signal = []
    boundaries = []

    current_type = rng.integers(len(segment_types))
    pos = 0

    with tqdm(total=int(total_samples), unit="samples", disable=not show_progress) as progress:
        while pos < total_samples:
            if rng.random() > p_repeat:
                current_type = rng.integers(len(segment_types))

            seg_len = rng.integers(min_len, max_len + 1)
            seg_len = min(seg_len, total_samples - pos)

            seg_type = segment_types[current_type]
            segment = create_segment_state(seg_type, seg_len, rng)
            x_seg = make_segment_chunk(segment, 0, seg_len, fs, rng, dtype=dtype)

            signal.append(x_seg)
            boundaries.append((pos, pos + seg_len, seg_type.name))

            pos += seg_len
            progress.update(int(seg_len))

    return np.concatenate(signal), boundaries


def generate_vibration_signal_memmap(
        output_path,
        fs=1000,
        total_samples=20000,
        min_len=100,
        max_len=3000,
        p_repeat=0.65,
        seed=0,
        dtype=np.float32,
        max_chunk_samples=10_000_000,
        show_progress=True,
):
    total_samples = int(total_samples)
    min_len = int(min_len)
    max_len = int(max_len)
    max_chunk_samples = int(max_chunk_samples)

    rng = np.random.default_rng()
    signal = open_memmap(output_path, mode="w+", dtype=dtype, shape=(total_samples,))
    boundaries = []

    current_type = rng.integers(len(segment_types))
    pos = 0

    with tqdm(total=total_samples, unit="samples", disable=not show_progress) as progress:
        while pos < total_samples:
            if rng.random() > p_repeat:
                current_type = rng.integers(len(segment_types))

            seg_len = int(rng.integers(min_len, max_len + 1))
            seg_len = min(seg_len, total_samples - pos)
            segment = create_segment_state(segment_types[current_type], seg_len, rng)
            segment_start = pos
            generated = 0

            while generated < seg_len:
                chunk_len = min(max_chunk_samples, seg_len - generated)
                chunk = make_segment_chunk(
                    segment,
                    start_offset=generated,
                    n=chunk_len,
                    fs=fs,
                    rng=rng,
                    dtype=dtype,
                )
                write_start = segment_start + generated
                signal[write_start:write_start + chunk_len] = chunk
                generated += chunk_len
                progress.update(int(chunk_len))

            boundaries.append((segment_start, segment_start + seg_len, segment.type.name))
            pos += seg_len

    signal.flush()
    del signal
    return boundaries, np.dtype(dtype).name, total_samples


def get_signal_folder(signal_length):
    human_len = humanize.intword(signal_length, format="%d")
    dataset_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "synthetic")
    subset_folder = os.path.join(dataset_folder, human_len)
    os.makedirs(subset_folder, exist_ok=True)
    return dataset_folder, subset_folder


def write_metadata(dataset_folder, subset_folder, signal_length, dtype):

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
      "total_sample_points": int(signal_length),
      "dtype": np.dtype(dtype).name,
      "display_as_delta": False
    }
    with open(os.path.join(subset_folder, "time.json"), "w") as f:
        f.write(json.dumps(time_json, indent=4))


def write_boundaries(boundaries, subset_folder):
    boundary_json = [
        {
            "start_index": int(start),
            "end_index": int(end),
            "length": int(end - start),
            "label": label,
        }
        for start, end, label in boundaries
    ]
    with open(os.path.join(subset_folder, "segment_boundaries.json"), "w") as f:
        f.write(json.dumps(boundary_json, indent=4))


def save_signal(signal, boundaries, dtype=None):
    dataset_folder, subset_folder = get_signal_folder(len(signal))
    write_metadata(dataset_folder, subset_folder, len(signal), signal.dtype if dtype is None else dtype)
    write_boundaries(boundaries, subset_folder)
    np.save(os.path.join(subset_folder, "values.npy"), signal)
    plot_segment_stripe(boundaries, os.path.join(subset_folder, "stripe.png"))


def save_signal_memmap(
        fs=1000,
        total_samples=20000,
        min_len=100,
        max_len=3000,
        p_repeat=0.65,
        seed=0,
        dtype=np.float32,
        max_chunk_samples=10_000_000,
        show_progress=True,
):
    dataset_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "synthetic")
    subset_folder = os.path.join(dataset_folder, "Experiment 1 (generating)")
    os.makedirs(subset_folder, exist_ok=True)
    output_path = os.path.join(subset_folder, "values.npy")

    boundaries, dtype_name, signal_length = generate_vibration_signal_memmap(
        output_path,
        fs=fs,
        total_samples=total_samples,
        min_len=min_len,
        max_len=max_len,
        p_repeat=p_repeat,
        seed=seed,
        dtype=dtype,
        max_chunk_samples=max_chunk_samples,
        show_progress=show_progress,
    )

    final_dataset_folder, final_subset_folder = get_signal_folder(total_samples)
    if os.path.abspath(subset_folder) != os.path.abspath(final_subset_folder):
        os.replace(output_path, os.path.join(final_subset_folder, "values.npy"))
        try:
            os.rmdir(subset_folder)
        except OSError:
            pass

    write_metadata(final_dataset_folder, final_subset_folder, signal_length, dtype_name)
    write_boundaries(boundaries, final_subset_folder)
    plot_segment_stripe(boundaries, os.path.join(final_subset_folder, "stripe.png"), fs=fs)
    return os.path.join(final_subset_folder, "values.npy"), boundaries


def ex1():
    total_length = 1_000_000
    save_signal_memmap(
        total_samples=total_length,
        min_len=10_000,
        max_len=200_000,
        max_chunk_samples=10_000_000,
        p_repeat=0.6
    )

def ex2():
    total_length = int(1e+10)
    save_signal_memmap(
        total_samples=total_length,
        min_len=100_000,
        max_len=100_000_000,
        max_chunk_samples=10_000_000,
        p_repeat=0.8
    )

if __name__ == '__main__':
    ex1()
