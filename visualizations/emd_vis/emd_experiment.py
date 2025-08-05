import matplotlib.pyplot as plt
import numpy as np
import emd

x = np.load("hydro.npy")
imf = emd.sift.sift(x)
print(imf.shape)

rows = imf.shape[1] + 1
fig, ax = plt.subplots(nrows=rows, ncols=1)
fig.set_size_inches(50, 10 * rows)

# print(imf[0])

for r in range(rows):
    if r == 0:
        ax[0].plot(x)
    else:
        ax[r].plot(imf[:, r - 1])

plt.savefig("emd.png")