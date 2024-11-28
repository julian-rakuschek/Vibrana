import os

import numpy as np
from matplotlib import pyplot as plt

import web.backend.helper.analysis as vibrana
from web.backend.modules.database import get_db
from web.backend.settings import chunks_folder


def normalize_distances(distances, normal_tube):
    tolerance = 2
    mean_normal = (normal_tube[0] + normal_tube[1]) / 2
    tube_radius = abs(normal_tube[0] - normal_tube[1]) / 2
    distances_to_mean_normal = np.abs(np.array(distances) - mean_normal)
    max_distance_from_mean = tube_radius * tolerance

    if max_distance_from_mean == 0 or np.isnan(max_distance_from_mean):
        return np.ones_like(distances_to_mean_normal)

    normalized = distances_to_mean_normal / max_distance_from_mean
    normalized = np.clip(normalized, 0, 1)
    return 1 - normalized


dataset = "nasa-bearings"
subset = "test2"
chunk = "2004.02.16.05.12.39-0000"

db = get_db()
labels = list(db["labels"].find({"dataset": dataset, "subset": subset}))
normals = db["normals"].find_one({"dataset": dataset, "subset": subset})

chunk_path = os.path.join(chunks_folder, dataset, subset, chunk)
distances = vibrana.compute_distance_profile(chunk_path, labels)
normal_tube = vibrana.compute_normal_tube(dataset, subset, labels, normals)
reduced = vibrana.reduce_distances(distances, normal_tube, 200, True)
normed1 = normalize_distances(distances, normal_tube)
normed2 = normalize_distances(reduced, normal_tube)

plot_mosaic = [
    ["values"],
    ["values"],
    ["values"],
    ["values"],
    ["similarities"],
    ["similarities"],
    ["similarities"],
    ["similarities"],
    ["colors1"],
    ["quantized"],
    ["quantized"],
    ["quantized"],
    ["quantized"],
    ["colors2"],
]

fig, ax = plt.subplot_mosaic(plot_mosaic)
plt.subplots_adjust(wspace=0, hspace=2)
fig.set_size_inches(30, 25)


values = np.load("motor-values.npy")
ax["values"].plot(values, color="black")
ax["values"].set_xlim((0, len(values)))
ax["values"].set_title("Vibration Signal of an Engine", fontsize=50)
ax["values"].spines[['right', 'top', 'bottom']].set_visible(False)
ax["values"].tick_params(bottom=False, labelbottom=False, labelsize=30)
ax["values"].set_ylabel("Acceleration", fontsize=40)

ax["similarities"].plot(distances, color="indigo")
ax["similarities"].set_xlim((0, len(distances)))
ax["similarities"].axhline(normal_tube[0], color="red")
ax["similarities"].axhline(normal_tube[1], color="red")
ax["similarities"].set_title("Distance profile with normal tube in red", fontsize=50)
ax["similarities"].spines[['right', 'top', 'bottom']].set_visible(False)
ax["similarities"].tick_params(bottom=False, labelbottom=False, labelsize=30)
ax["similarities"].set_ylabel("Distance", fontsize=40)

ax["quantized"].plot(reduced, color="indigo")
ax["quantized"].set_xlim((0, len(reduced)))
ax["quantized"].axhline(normal_tube[0], color="red")
ax["quantized"].axhline(normal_tube[1], color="red")
ax["quantized"].set_title("The post-processed distance profile using quantization", fontsize=50)
ax["quantized"].spines[['right', 'top', 'bottom']].set_visible(False)
ax["quantized"].tick_params(bottom=False, labelbottom=False)
ax["quantized"].tick_params(bottom=False, labelbottom=False, labelsize=30)
ax["quantized"].set_ylabel("Distance", fontsize=40)

ax["colors1"].pcolormesh(np.array([normed1]), cmap="RdYlBu")
ax["colors1"].set_axis_off()

ax["colors2"].pcolormesh(np.array([normed2]), cmap="RdYlBu")
ax["colors2"].set_axis_off()

plt.savefig(f"quantization.png", bbox_inches='tight', dpi=200)
