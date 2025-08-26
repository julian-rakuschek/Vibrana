import json

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import jensenshannon
from incdbscan import IncrementalDBSCAN
from sklearn.manifold import MDS

with open("incdbscan_data.json", "r") as f:
    vectors = json.load(f)
feature_descriptors = []
for v in vectors:
    feature_descriptors.append(v["feature_descriptors"]["radii_distribution"]["counts"])
feature_descriptors = np.array(feature_descriptors)
print(feature_descriptors)
print(feature_descriptors.shape)

similarity_matrix = np.zeros((feature_descriptors.shape[0], feature_descriptors.shape[0]))
print(similarity_matrix.shape)
for i, p in enumerate(feature_descriptors):
    for j, q in enumerate(feature_descriptors):
        similarity_matrix[i, j] = jensenshannon(p, q)
print(similarity_matrix)

projected = MDS(n_components=2, dissimilarity="precomputed").fit_transform(similarity_matrix)
clusterer = IncrementalDBSCAN(eps=0.2, min_pts=5, metric="jensenshannon")

clusterer.insert(feature_descriptors)
labels = clusterer.get_cluster_labels(feature_descriptors)
print(labels)

plt.scatter(projected[:, 0], projected[:, 1], c=labels, cmap='rainbow')
plt.savefig("projected.png")

print(similarity_matrix[0])
