import os
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

chunk_path = os.path.join(Path(__file__).parents[2], "data", "chunks-original", "nasa-bearings", "test2")

for chunk in os.listdir(chunk_path):
    plt.clf()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(10, 10)
    projected = np.load(os.path.join(chunk_path, chunk, "projected.npy"))
    ax.set_xlim([np.min(projected[:, 0]), np.max(projected[:, 0])])
    ax.set_ylim([np.min(projected[:, 1]), np.max(projected[:, 1])])
    ax.scatter(projected[:, 0], projected[:, 1], s=5, c="#4A148C")
    ax.axis("off")
    plt.savefig(f"plots3/{chunk}.png", bbox_inches='tight', dpi=300, transparent=True)
    plt.close(fig)