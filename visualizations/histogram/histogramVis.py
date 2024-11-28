import numpy as np
from matplotlib import pyplot as plt, patches
from matplotlib.pyplot import colormaps

label_font_size = 30

cloud1 = np.load("projected-engine-healthy.npy")
cloud2 = np.load("projected-engine-damaged.npy")

radii1 = np.linalg.norm(cloud1, axis=1)
radii2 = np.linalg.norm(cloud2, axis=1)
max_radius = max(np.max(radii1), np.max(radii2))

counts1, bins1 = np.histogram(radii1, bins=10, range=(0, max_radius), density=True)
counts2, bins2 = np.histogram(radii2, bins=10, range=(0, max_radius), density=True)
colors = colormaps["turbo"](bins1 / max_radius)
step_size = float(bins1[1])
print(colors)
print(bins2)

plot_mosaic = [
    ["cloud1", "hist1"],
    ["cloud2", "hist2"],
]

fig, ax = plt.subplot_mosaic(plot_mosaic)
plt.subplots_adjust(wspace=0.35, hspace=0.2)
fig.set_size_inches(20, 20)

ax["cloud1"].set_title("Radius Segments of \n the Point Cloud", fontsize=label_font_size)
ax["hist1"].set_title("Histogram of Radius \n Distribution Among Points", fontsize=label_font_size)

ax["cloud1"].scatter(cloud1[:, 0], cloud1[:, 1], s=1, c="black")
ax["cloud1"].tick_params(axis='both', which='major', labelsize=25)
ax["cloud1"].set_xlabel("Radius X", fontsize=label_font_size)
ax["cloud1"].set_ylabel("Radius Y", fontsize=label_font_size)
ax["cloud1"].set_xlim([-max_radius, max_radius])
ax["cloud1"].set_ylim([-max_radius, max_radius])
for idx, bin in enumerate(bins1):
    if idx == 0:
        continue
    ax["cloud1"].add_patch(patches.Annulus((0, 0), bin, step_size, alpha=0.6, color=colors[idx]))

ax["cloud2"].scatter(cloud2[:, 0], cloud2[:, 1], s=1, c="black")
ax["cloud2"].tick_params(axis='both', which='major', labelsize=25)
ax["cloud2"].set_xlabel("Radius X", fontsize=label_font_size)
ax["cloud2"].set_ylabel("Radius Y", fontsize=label_font_size)
ax["cloud2"].set_xlim([-max_radius, max_radius])
ax["cloud2"].set_ylim([-max_radius, max_radius])
for idx, bin in enumerate(bins2):
    if idx == 0:
        continue
    ax["cloud2"].add_patch(patches.Annulus((0, 0), bin, step_size, alpha=0.6, color=colors[idx]))

ax["hist1"].bar(bins1[1:], counts1, width=step_size, color=colors[1:])
ax["hist1"].set_xlabel("Radius", fontsize=label_font_size)
ax["hist1"].set_ylabel("Ratio of Points", fontsize=label_font_size)
ax["hist2"].bar(bins2[1:], counts2, width=step_size, color=colors[1:])
ax["hist2"].set_xlabel("Radius", fontsize=label_font_size)
ax["hist2"].set_ylabel("Ratio of Points", fontsize=label_font_size)
ax["hist1"].tick_params(axis='both', which='major', labelsize=25)
ax["hist2"].tick_params(axis='both', which='major', labelsize=25)
plt.savefig(f"histogram.png", bbox_inches='tight', dpi=200)
