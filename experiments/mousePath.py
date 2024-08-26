import copy

import numpy as np
from matplotlib import pyplot as plt
import alphashape
from matplotlib.patches import Polygon
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import shapely
import Polygon as gpc

# Plots a Polygon to pyplot `ax`
def plot_polygon(ax, poly, **kwargs):
    path = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)

    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

def apply_brush(curve, radius, n_points_per_point):
    res = []
    for point in curve:
        for i in range(n_points_per_point):
            x = point[0] + np.cos(i/n_points_per_point * 2 * np.pi) * radius
            y = point[1] + np.sin(i/n_points_per_point * 2 * np.pi) * radius
            res.append((x, y))
    res = np.array(res)
    return res


def brush_alpha():
    curve = np.load("Curve_0.npy")
    brushed = apply_brush(curve, 12, 15)
    fig, ax = plt.subplots()
    ax.scatter(brushed[:, 0], brushed[:, 1], s=1)
    ax.scatter(curve[:, 0], curve[:, 1])
    alpha_shape = alphashape.alphashape(brushed, 0.2)
    print(alpha_shape)
    if alpha_shape.geom_type == 'MultiPolygon':
        Polygons = list(alpha_shape.geoms)
        for p in Polygons:
            plot_polygon(ax, p, facecolor='purple', edgecolor='purple', alpha=0.5)
    elif alpha_shape.geom_type == 'Polygon':
        plot_polygon(ax, alpha_shape, facecolor='purple', edgecolor='purple', alpha=0.5)
    plt.show()


def brush_iterative_gpc():
    curve = np.load("Curve_0.npy")
    brushed = None
    for p in curve:
        brushed_p = apply_brush([p], 12, 15)
        polygon = gpc.Polygon(brushed_p.tolist())
        if brushed is None:
            brushed = copy.deepcopy(polygon)
        else:
            # m = MultiPolygon([brushed, polygon])
            brushed += polygon
    fig, ax = plt.subplots()
    # ax.scatter(brushed[:, 0], brushed[:, 1], s=1)
    ax.scatter(curve[:, 0], curve[:, 1])
    print(brushed)
    for poly in brushed:
        print(poly)
        plot_polygon(ax, shapely.Polygon(poly), facecolor='purple', edgecolor='purple', alpha=0.5)
    plt.show()


def brush_iterative_shapely():
    curve = np.load("Curve_0.npy")
    brushed = None
    for p in curve:
        brushed_p = apply_brush([p], 12, 15)
        polygon = shapely.Polygon(brushed_p.tolist())
        if brushed is None:
            brushed = copy.deepcopy(polygon)
        else:
            # m = MultiPolygon([brushed, polygon])
            brushed = shapely.union(polygon, brushed)
    fig, ax = plt.subplots()
    # ax.scatter(brushed[:, 0], brushed[:, 1], s=1)
    ax.scatter(curve[:, 0], curve[:, 1])
    print(brushed.exterior)
    print(brushed.interiors)
    if brushed.geom_type == 'MultiPolygon':
        Polygons = list(brushed.geoms)
        for p in Polygons:
            plot_polygon(ax, p, facecolor='purple', edgecolor='purple', alpha=0.5)
    elif brushed.geom_type == 'Polygon':
        plot_polygon(ax, brushed, facecolor='purple', edgecolor='purple', alpha=0.5)
    plt.show()

def triangle_approach():
    curve = np.load("Curve_0.npy")
    for p in curve:
        brushed_p = apply_brush([p], 12, 15)
        polygon = shapely.Polygon(brushed_p.tolist())
        if brushed is None:
            brushed = copy.deepcopy(polygon)
        else:
            # m = MultiPolygon([brushed, polygon])
            brushed = shapely.union(polygon, brushed)

if __name__ == '__main__':
    brush_iterative_gpc()