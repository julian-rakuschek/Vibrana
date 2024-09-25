import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA


def to_2d_cloud(values):
    windows = sliding_window_view(values, window_shape=100)
    projected = PCA(n_components=2, svd_solver="full").fit_transform(windows)
    return projected


# Parameters for the sine waves
sampling_rate = 1000  # Samples per second
duration = 1  # Duration of the signal in seconds

# Frequency of the sine waves
freq1 = 5  # Frequency of the first sine wave in Hz
freq2 = 10 # Frequency of the second sine wave in Hz

# Time vector
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generating the sine waves
sine_wave1 = np.sin(2 * np.pi * freq1 * t)
sine_wave2 = np.sin(2 * np.pi * freq2 * t)

# Combining the sine waves
combined_wave = sine_wave1 + sine_wave2

# Plotting the sine waves and their combination
plt.clf()
fig, ax = plt.subplots(nrows=3, ncols=2)
fig.set_size_inches(30, 20)
# Plot first sine wave
ax[0, 0].plot(t, sine_wave1, label=f'Sine Wave 1: {freq1} Hz')
ax[0, 0].set_title('Sine Wave 1')
proj = to_2d_cloud(sine_wave1)
ax[0, 1].scatter(proj[:, 0], proj[:, 1])

# Plot second sine wave
ax[1, 0].plot(t, sine_wave2, label=f'Sine Wave 2: {freq2} Hz', color='orange')
ax[1, 0].set_title('Sine Wave 2')
proj = to_2d_cloud(sine_wave2)
ax[1, 1].scatter(proj[:, 0], proj[:, 1], color='orange')

# Plot combined wave
ax[2, 0].plot(t, combined_wave, label='Combined Wave', color='green')
ax[2, 0].set_title('Combined Sine Wave')
proj = to_2d_cloud(combined_wave)
ax[2, 1].scatter(proj[:, 0], proj[:, 1], color='green')

# Display the plots
plt.tight_layout()
# plt.show()
plt.savefig("mix_freq.png")
