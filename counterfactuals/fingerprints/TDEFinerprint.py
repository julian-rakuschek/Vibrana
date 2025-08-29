import emd
import numpy as np
from numpy.lib._stride_tricks_impl import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def compute_tde(data, w):
    windows = sliding_window_view(data, window_shape=w)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)
    return projected

class TDEFingerprint:
    def __init__(self, data, w):
        self.data = data
        self.w = w
        self.projected = compute_tde(data, w)
        self.imf = emd.sift.sift(data)
        self.perturbations = []

    def get_histogram(self, max=None):
        radii = np.linalg.norm(self.projected, axis=1)
        if max is None:
            max = np.max(radii)
        counts, bins = np.histogram(radii, bins=20, range=(0, max), density=True)
        return counts, bins

