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

    def clear(self):
        pass

