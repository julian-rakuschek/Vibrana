import numpy as np
from matplotlib import pyplot as plt

values = np.load("/home/vulturemox/Coding/PhD/PRESENT/Vibrana/data/chunks/motor/inner-damage/inner-12-0000/projected.npy")
values = np.load("/home/vulturemox/Coding/PhD/PRESENT/Vibrana/data/chunks/motor/inner-damage/undagamed-07-0000/projected.npy")
values = np.load("/home/vulturemox/Coding/PhD/PRESENT/Vibrana/data/chunks/motor/inner-damage/inner-02-0000/projected.npy")
radii = np.linalg.norm(values, axis=1)
print(radii)
counts, bins = np.histogram(radii, bins=10, range=(0, np.max(radii)), density=True)
print(counts)

plt.stairs(counts, bins)
plt.show()