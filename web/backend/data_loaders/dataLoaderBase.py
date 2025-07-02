import numpy as np


class DataLoaderBase:
    def __init__(self):
        self.data_size = 0
        self.redis_prefix = ""
        pass

    def load_numpy_file(self, overwrite_existing=False):
        pass

    def get_slice(self, start=0, end=-1):
        pass

    def store_hyperplane_vectors(self, v1: np.ndarray, v2: np.ndarray, start: int, window_size: int):
        pass

    def retrieve_hyperplane_vectors(self, start: int = None, window_size: int = None):
        pass

    def set_target_threads(self, num_threads):
        pass

    def get_target_threads(self):
        pass

    def clear(self):
        pass

