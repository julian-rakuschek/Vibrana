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


def _get_segment_type(segment_type):
    if isinstance(segment_type, SegmentType):
        return segment_type

    for candidate in segment_types:
        if candidate.name == segment_type:
            return candidate

    raise ValueError(f"Unknown segment type: {segment_type}")


def _describe_segment_type(seg_type):
    if seg_type.kind == "sine":
        return f"{seg_type.name}: {seg_type.freqs[0]} Hz sine"
    if seg_type.kind == "multi_sine":
        freqs = " + ".join(f"{freq} Hz" for freq in seg_type.freqs)
        return f"{seg_type.name}: {freqs}"
    if seg_type.kind == "chirp":
        return f"{seg_type.name}: {seg_type.freqs[0]}-{seg_type.freqs[1]} Hz chirp"
    if seg_type.kind == "noise":
        return f"{seg_type.name}: broadband noise"
    return f"{seg_type.name}: {seg_type.kind}"


def _normalise_plot_color(color):
    if not isinstance(color, str) or not color.startswith("rgb(") or not color.endswith(")"):
        return color

    channels = [int(channel.strip()) for channel in color[4:-1].split(",")]
    return tuple(channel / 255 for channel in channels)


def plot_segment_type_fft_showcase(
        segment_type,
        path=None,
        fs=1000,
        length=1000,
        color="black",
        figsize=(2.0, 1.45),
        ax=None,
        seed=0,
        title=None,
        dpi=180,
):
    seg_type = _get_segment_type(segment_type)
    rng = np.random.default_rng(seed)
    segment = create_segment_state(seg_type, length, rng)
    signal = make_segment_chunk(segment, 0, length, fs, rng)

    frequencies = np.fft.rfftfreq(len(signal), d=1.0 / fs)
    magnitudes = np.abs(np.fft.rfft(signal))
    if np.max(magnitudes) > 0:
        magnitudes = magnitudes / np.max(magnitudes)

    owns_figure = ax is None
    if owns_figure:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    color = _normalise_plot_color(color)
    ax.plot(frequencies, magnitudes, color=color, linewidth=1.1)
    ax.fill_between(frequencies, magnitudes, color=color, alpha=0.14, linewidth=0)
    ax.set_xlim(0, fs / 2)
    ax.set_ylim(0, 1.05)
    ax.set_title(title or _describe_segment_type(seg_type), fontsize=8, pad=3)
    ax.set_xlabel("Hz", fontsize=7, labelpad=1)
    ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=6, length=2, pad=1)
    ax.tick_params(axis="y", length=0)
    ax.margins(x=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_linewidth(0.6)

    if owns_figure:
        fig.tight_layout(pad=0.25)
        if path is not None:
            fig.savefig(path, bbox_inches="tight", dpi=dpi)
            plt.close(fig)

    return fig, ax


def plot_segment_stripe(boundaries, path, fs=1.0, figsize=(100, 2), label_to_color=None):
    labels_unique = sorted(set(label for _, _, label in boundaries))
    cmap = plt.get_cmap("tab10", len(labels_unique))
    if label_to_color is None:
        label_to_color = {lab: cmap(i) for i, lab in enumerate(labels_unique)}
    fig, ax = plt.subplots(figsize=figsize)
    for start, end, label in boundaries:
        start_t = start / fs
        width = (end - start) / fs
        ax.barh(y=0, width=width, left=start_t, height=1, align="edge", color=label_to_color.get(label, "gray"))
    min_start = min(start for start, _, _ in boundaries) / fs
    max_end = max(end for _, end, _ in boundaries) / fs
    ax.set_xlim(min_start, max_end)
    ax.margins(x=0)
    ax.set_yticks([])
    ax.set_xlabel("Time [s]")
    ax.set_title("Segment Structure")
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=label_to_color.get(l, "gray"))
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


def plot_signal_preview(values_path, output_path, total_samples, fs=1000, max_points=50_000):
    signal = np.load(values_path, mmap_mode="r")
    stride = max(1, int(np.ceil(total_samples / max_points)))
    y = signal[::stride]
    x = np.arange(0, total_samples, stride)[:len(y)] / fs

    fig, ax = plt.subplots(figsize=(18, 4))
    ax.plot(x, y, linewidth=0.4, color="black")
    ax.set_xlim(0, total_samples / fs)
    ax.margins(x=0)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.set_title("Signal Preview")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=180)
    plt.close(fig)


def generate_sandwich_signal(
        fs=1000,
        total_samples=100_000_000,
        middle_segment_len=20_000,
        seed=0,
        dtype=np.float32,
        max_chunk_samples=1_000_000,
        show_progress=True,
):
    total_samples = int(total_samples)
    middle_segment_len = int(middle_segment_len)
    max_chunk_samples = int(max_chunk_samples)

    if total_samples <= 0:
        raise ValueError("total_samples must be positive")
    if middle_segment_len <= 0:
        raise ValueError("middle_segment_len must be positive")

    middle_len = 3 * middle_segment_len
    if middle_len >= total_samples:
        raise ValueError("3 * middle_segment_len must be smaller than total_samples")

    rng = np.random.default_rng(seed)
    dataset_folder = os.path.join(Path(__file__).parents[1], "data", "prepared-signals", "synthetic")
    subset_folder = os.path.join(dataset_folder, "sandwich")
    os.makedirs(subset_folder, exist_ok=True)

    output_path = os.path.join(subset_folder, "values.npy")
    signal = open_memmap(output_path, mode="w+", dtype=dtype, shape=(total_samples,))

    left_noise_len = (total_samples - middle_len) // 2
    right_noise_len = total_samples - left_noise_len - middle_len
    middle_start = left_noise_len

    layout = [
        (0, left_noise_len, SegmentType("Noise", "noise", amp=0.0, noise_std=0.8)),
        (middle_start, middle_start + middle_segment_len,
         SegmentType("Sine 30 Hz", "sine", freqs=(30,), amp=1.4, noise_std=0.05)),
        (middle_start + middle_segment_len, middle_start + 2 * middle_segment_len,
         SegmentType("Multi Sine", "multi_sine", freqs=(65, 140, 220), amp=1.2, noise_std=0.05)),
        (middle_start + 2 * middle_segment_len, middle_start + middle_len,
         SegmentType("Chirp", "chirp", freqs=(20, 250), amp=1.3, noise_std=0.05)),
        (middle_start + middle_len, total_samples, SegmentType("Noise", "noise", amp=0.0, noise_std=0.8)),
    ]

    boundaries = []
    with tqdm(total=total_samples, unit="samples", disable=not show_progress) as progress:
        for start, end, seg_type in layout:
            segment = create_segment_state(seg_type, end - start, rng)
            generated = 0
            while start + generated < end:
                chunk_len = min(max_chunk_samples, end - start - generated)
                chunk = make_segment_chunk(
                    segment,
                    start_offset=generated,
                    n=chunk_len,
                    fs=fs,
                    rng=rng,
                    dtype=dtype,
                )
                write_start = start + generated
                signal[write_start:write_start + chunk_len] = chunk
                generated += chunk_len
                progress.update(int(chunk_len))
            boundaries.append((start, end, seg_type.name))

    signal.flush()
    del signal

    dtype_name = np.dtype(dtype).name
    write_metadata(dataset_folder, subset_folder, total_samples, dtype_name)
    write_boundaries(boundaries, subset_folder)
    plot_segment_stripe(boundaries, os.path.join(subset_folder, "stripe.png"), fs=fs, figsize=(18, 2))
    plot_signal_preview(output_path, os.path.join(subset_folder, "signal.png"), total_samples, fs=fs)

    return output_path, boundaries


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


def plot_all_segment_type_fft_showcases(
        path=None,
        fs=1000,
        length=1000,
        colors=None,
        figsize=(20, 1.45),
        seed=0,
        dpi=180,
):
    if colors is None:
        cmap = plt.get_cmap("tab10", len(segment_types))
        colors = {seg_type.name: cmap(i) for i, seg_type in enumerate(segment_types)}

    fig, axes = plt.subplots(1, len(segment_types), figsize=figsize, sharey=True)
    for i, (ax, seg_type) in enumerate(zip(np.atleast_1d(axes), segment_types)):
        if isinstance(colors, dict):
            color = colors.get(seg_type.name, "black")
        else:
            color = colors[i]

        plot_segment_type_fft_showcase(
            seg_type,
            fs=fs,
            length=length,
            color=color,
            ax=ax,
            seed=seed,
        )

    fig.tight_layout(pad=0.25, w_pad=0.4)
    if path is not None:
        fig.savefig(path, bbox_inches="tight", dpi=dpi)
        plt.close(fig)

    return fig, axes


if __name__ == '__main__':
    label_map_fft = {
        "A": "rgb(218, 4, 160)",
        "B": "rgb(37, 251, 95)",
        "C": "rgb(255, 64, 64)",
        "D": "rgb(0, 191, 191)",
        "E": "rgb(127, 17, 238)",
        "F": "rgb(176, 205, 1)",
        "G": "rgb(127, 238, 17)",
        "H": "rgb(218, 160, 4)",
        "I": "rgb(245, 111, 26)",
        "J": "rgb(127, 238, 17)",
    }
    plot_all_segment_type_fft_showcases(path="types.png", colors=label_map_fft)
