import os.path
import os.path

import numpy as np
import scipy.cluster.hierarchy as hierarchy
from pymongo.synchronous.database import Database

from vibrana.algorithms.incdbscan import IncrementalDBSCAN
from vibrana.backend.settings import chunks_folder
import vibrana.backend.helper.database as database


def compute_clusters_hierarchical(dataset, subset):
    def convert_tree(node, labels):
        if node.left is None and node.right is None:
            return {"id": labels[node.id]}
        left = convert_tree(node.left, labels)
        right = convert_tree(node.right, labels)
        return {"id": node.id, "dist": node.dist, "left": left, "right": right}

    subset_path = str(os.path.join(chunks_folder, dataset, subset))
    histograms = []
    chunks = []
    all_radii = []
    max_radius = 0
    for file in os.listdir(subset_path):
        chunks.append(file)
        projected = np.load(os.path.join(subset_path, file, "projected.npy"))
        radii = np.linalg.norm(projected, axis=1)
        all_radii.append(radii)
        max_radius = max(max_radius, np.max(radii))
    for radii in all_radii:
        counts, bins = np.histogram(radii, bins=50, range=(0, max_radius), density=True)
        histograms.append(counts)
    histograms = np.array(histograms)
    clustering = hierarchy.linkage(histograms, method='complete', metric="jensenshannon")
    linkage_tree = hierarchy.to_tree(clustering)
    json_tree = convert_tree(linkage_tree, chunks)
    return json_tree


