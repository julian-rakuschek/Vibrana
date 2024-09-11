import numpy as np
import requests
from matplotlib import pyplot as plt

# test = requests.post("http://localhost:5000/api/db/labels/dummy", json={"from": 400, "to": 800})
# test = requests.post("http://localhost:5000/api/db/labels/dummy", json={"from": 900, "to": 1800})
# test = requests.delete("http://localhost:5000/api/db/labels/dummy", json={"index": 901})

abnormal = requests.get("http://localhost:5000/api/analysis/5-10-1t-10-16/abnormal-0002/similarities").json()
normal = requests.get("http://localhost:5000/api/analysis/5-10-1t-10-16/normal-0002/similarities").json()

fig, ax = plt.subplots(nrows=2, ncols=1)
fig.set_size_inches(40, 10)

ax[0].plot(np.arange(len(normal)), normal, color="black")
ax[0].set_title("Normal", fontsize=20)
ax[0].set_xlim([0, len(normal)])

ax[1].plot(np.arange(len(abnormal)), abnormal, color="black")
ax[1].set_title("Abnormal", fontsize=20)
ax[1].set_xlim([0, len(abnormal)])

plt.show()