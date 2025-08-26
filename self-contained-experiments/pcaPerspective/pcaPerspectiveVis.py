import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import colormaps
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def compute_projection():
    values = np.load("values.npy")
    windows = sliding_window_view(values, window_shape=2_000)
    windows = StandardScaler().fit_transform(windows)
    projected = PCA(n_components=2).fit_transform(windows)
    np.save("projected2D.npy", projected)
    projected = PCA(n_components=3).fit_transform(windows)
    np.save("projected3D.npy", projected)
    # scores = []
    # for point in projected:
    #     scores.append(np.linalg.norm(point))
    # scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]


def plot_projection():
    fig = plt.figure(figsize=(20, 10))
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    # Create a 1x2 subplot structure with the second subplot being 3D
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122, projection='3d')

    # Load and process the 2D projection
    projected_2d = np.load("projected2D.npy")
    scores_2d = [np.linalg.norm(point) for point in projected_2d]
    scores_2d_norm = MinMaxScaler().fit_transform(np.array(scores_2d).reshape(-1, 1))[:, 0]

    ax1.scatter(projected_2d[:, 0], projected_2d[:, 1], s=8, c=colormaps["turbo"](scores_2d_norm))
    ax1.set_title("TDE with 2D Projection", fontsize=30)
    ax1.axis("off")

    # Load and process the 3D projection
    projected_3d = np.load("projected3D.npy")
    scores_3d = [np.linalg.norm(point) for point in projected_3d]
    scores_3d_norm = MinMaxScaler().fit_transform(np.array(scores_3d).reshape(-1, 1))[:, 0]

    # Add a 3D scatterplot to the second subplot
    ax2.scatter(projected_3d[:, 0], projected_3d[:, 1], projected_3d[:, 2], s=8, c=colormaps["turbo"](scores_3d_norm))
    ax2.set_title("TDE with 3D Projection", fontsize=30)
    ax2.view_init(elev=20, azim=25)

    # Save the figure
    plt.savefig(f"pca.png", bbox_inches='tight', dpi=100)


if __name__ == '__main__':
    compute_projection()
    plot_projection()
