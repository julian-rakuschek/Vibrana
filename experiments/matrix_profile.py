import numpy as np
from matplotlib import pyplot as plt

mat = np.load("matrix.npy", allow_pickle=True)
print(mat)

values = mat[:, 0]
print(values)
plt.plot(values)
plt.show()