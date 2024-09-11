import numpy as np
import requests
from matplotlib import pyplot as plt


def normalize_array(arr, min_value, max_value):
    normalized = (arr - min_value) / (max_value - min_value)
    return normalized


# test = requests.post("http://localhost:5000/api/db/labels/dummy", json={"from": 400, "to": 800})
# test = requests.post("http://localhost:5000/api/db/labels/dummy", json={"from": 900, "to": 1800})
# test = requests.delete("http://localhost:5000/api/db/labels/dummy", json={"index": 901})

abnormal = requests.get("http://localhost:5000/api/analysis/5-10-1t-10-16/abnormal-0004/similarities").json()
normal = requests.get("http://localhost:5000/api/analysis/5-10-1t-10-16/normal-0002/similarities").json()
normal_tube = requests.get("http://localhost:5000/api/analysis/5-10-1t-10-16/normal_band").json()

fig, ax = plt.subplots(nrows=3, ncols=1)
fig.set_size_inches(40, 15)

ax[0].plot(np.arange(len(normal)), normal, color="black")
ax[0].set_title("Normal", fontsize=20)
ax[0].set_xlim([0, len(normal)])
ax[0].axhline(normal_tube[0], linestyle='--', c="red")
ax[0].axhline(normal_tube[1], linestyle='--', c="red")

ax[1].plot(np.arange(len(abnormal)), abnormal, color="black")
ax[1].set_title("Abnormal", fontsize=20)
ax[1].set_xlim([0, len(abnormal)])
ax[1].axhline(normal_tube[0], linestyle='--', c="red")
ax[1].axhline(normal_tube[1], linestyle='--', c="red")

norm = normalize_array(np.array(abnormal), normal_tube[0], normal_tube[1])
print(norm)
ax[2].plot(np.arange(len(norm)), norm, color="black")
ax[2].set_title("Abnormal normalized", fontsize=20)
ax[2].set_xlim([0, len(norm)])
plt.show()

print(normal_tube)