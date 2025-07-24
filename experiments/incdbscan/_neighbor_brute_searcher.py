import numpy as np
from scipy.spatial.distance import jensenshannon
from sklearn.neighbors import NearestNeighbors
from sortedcontainers import SortedList


class NeighborBruteSearch:
    def __init__(self, radius):
        self.values = np.array([])
        self.ids = SortedList()
        self.radius = radius

    def insert(self, new_value, new_id):
        self.ids.add(new_id)
        position = self.ids.index(new_id)
        self._insert_into_array(new_value, position)

    def _insert_into_array(self, new_value, position):
        extended = np.insert(self.values, position, new_value, axis=0)
        if not self.values.size:
            extended = extended.reshape(1, -1)
        self.values = extended

    def query_neighbors(self, query_value):
        found_neighbors = []
        for idx, item in enumerate(self.values):
            dist = jensenshannon(query_value, item)
            if dist <= self.radius:
                found_neighbors.append(self.ids[idx])
        return found_neighbors

    def delete(self, id_):
        position = self.ids.index(id_)
        del self.ids[position]
        self.values = np.delete(self.values, position, axis=0)
