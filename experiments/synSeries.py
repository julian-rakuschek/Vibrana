import math
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from algorithms.timeseries_dgan.dgan import DGAN
from algorithms.timeseries_dgan.config import DGANConfig
from gutenTAG import GutenTAG

def get_base_ts(name="dirichlet-sine"):
    frequency = 1000
    # variance = np.random.normal(loc=0.1, scale=0.02)
    variance = 0.1
    amplitude = 0.5
    return {
        "name": "test",
        "length": 1000,
        "base-oscillations": [
            {
                "kind": "dirichlet",
                "frequency": frequency,
                "variance": variance,
                "amplitude": amplitude,
            },
        ],
        "semi-supervised": True,
        "supervised": False,
        "anomalies": []
    }

def example_ts():
    gutentag = GutenTAG()
    config = {"timeseries": []}
    ts = get_base_ts()
    config["timeseries"].append(ts)
    gutentag.load_config_dict(config)
    datasets = gutentag.generate(return_timeseries=True)
    df = datasets[0].timeseries
    df.drop(columns=["is_anomaly"], inplace=True)
    return df.to_numpy()

base_path = os.path.join(Path(__file__).parents[1], "data")
all_values = []
lengths = []
for folder in os.listdir(base_path):
    print(folder)
    if os.path.exists(os.path.join(base_path, folder, "values.npy")):
        values = np.load(os.path.join(base_path, folder, "values.npy"))
        print(len(values))
        lengths.append(len(values))
        all_values.append(values)
min_length = min(lengths)
all_values = np.array([values[:min_length] for values in all_values])

# ts = [example_ts() for _ in range(20)]
features: np.ndarray = np.array(all_values)
features = features.reshape(features.shape[0], features.shape[1], 1)
print(features.shape)
divisors = [i for i in range(1, math.floor(math.sqrt(min_length))) if min_length % i == 0]
config = DGANConfig(
    max_sequence_len=features.shape[1],
    sample_len=divisors[-1],
    batch_size=1000,
    epochs=1000
)
model = DGAN(config)

model.train_numpy(attributes=None, features=features)
print("Train Done")
synthetic_attributes, synthetic_features = model.generate_numpy(1)
generated = synthetic_features[0]
print(generated.shape)
print("Test Done")

print(generated)
plt.plot(features[0, :, 0], color='blue')
plt.plot(generated[:, 0], color='orange')
plt.show()