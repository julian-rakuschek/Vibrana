import RBush from "rbush";
import {Pair, Polygon} from "polygon-clipping";
import earcut from "earcut";
import {Earcut, ProjectedPoint} from "../types";
import {euclidean} from "lib/geometryUtil";

export class DemoRBush extends RBush<[number, number, number]> {
    toBBox([x, y, index]: [number, number, number]) {
        return {minX: x, minY: y, maxX: x, maxY: y};
    }

    compareMinX(a, b) {
        return a.x - b.x;
    }

    compareMinY(a, b) {
        return a.y - b.y;
    }

    find(x: number, y: number, radius: number): number[][] {
        const init_res = this.search({
            minX: x - radius,
            minY: y - radius,
            maxX: x + radius,
            maxY: y + radius
        })
        return init_res.filter(p => Math.sqrt(euclidean({x: p[0], y: p[1]}, {x, y})) < radius)
    }
}

export class ProjectedTimeSeriesRBush extends RBush<ProjectedPoint> {
    toBBox(point: ProjectedPoint) {
        return {minX: point.coords[0], minY: point.coords[1], maxX: point.coords[0], maxY: point.coords[1]};
    }

    compareMinX(a, b) {
        return a.x - b.x;
    }

    compareMinY(a, b) {
        return a.y - b.y;
    }

    find(x: number, y: number, radius: number): ProjectedPoint[] {
        const init_res = this.search({
            minX: x - radius,
            minY: y - radius,
            maxX: x + radius,
            maxY: y + radius
        })
        return init_res.filter(p =>Math.sqrt( euclidean({x: p.coords[0], y: p.coords[1]}, {x, y})) < radius)
    }

    findBox(minX: number, maxX: number, minY: number, maxY: number): ProjectedPoint[] {
         return this.search({minX, minY, maxX, maxY})
    }
}

export const getCirlcePoints = (coords: [number, number], radius: number, n: number): Polygon => {
    const points: Pair[] = []
    for (let i = 0; i < n; i++) {
        const x = Math.cos(i / n * Math.PI * 2) * radius + coords[0];
        const y = Math.sin(i / n * Math.PI * 2) * radius + coords[1];
        points.push([x, y])
    }
    points.push([points[0][0], points[0][1]])
    return [points];
}


export const polyToEarcut = (poly: Polygon): Earcut => {
    const flat: number[] = poly.flat(Infinity) as number[];
    const lenghts = poly.map(ring => ring.length);
    const indices = lenghts.map(((sum: number) => (value: number) => sum += value)(0));
    indices.pop()
    return {
        vertices: flat,
        hole_indices: indices
    }
}

export const polyToTriangles = (poly: Polygon): number[][][] => {
    const flatToTriangles = (arr: number[]) => {
        const polyFlat = poly.flat(1)
        const result = [];
        for (let i = 0; i < arr.length; i += 3) {
            result.push([
                polyFlat[arr[i]],
                polyFlat[arr[i + 1]],
                polyFlat[arr[i + 2]],
                polyFlat[arr[i]]
            ]);
        }
        return result;
    };


    const t = polyToEarcut(poly)
    const tria = earcut(t.vertices, t.hole_indices)
    return flatToTriangles(tria)
}

export const mousePolygon = (x: number, y: number, button: number, radius: number): number[][][] => {
    const points = getCirlcePoints([x, y], radius, 20);
    const triang = polyToTriangles(points);
    return triang.map(t => t.map(p => [...p, button]))
}
