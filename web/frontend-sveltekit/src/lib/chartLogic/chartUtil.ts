import type {ProjectedPoint} from "@lib/types";
import * as d3 from "d3";

export const moveMiddleToEnd = (data: ProjectedPoint[], range: number[] | null): ProjectedPoint[] => {
    if (range === null) return data;
    const [start, end] = range;
    const middlePart = data.slice(start, end);
    return data.slice(0, start).concat(data.slice(end), middlePart);
}

export const compute_quadtree = (data: ProjectedPoint[], filterRange: [number, number] | null): d3.Quadtree<ProjectedPoint> => {
    const filteredData = filterRange ? data.filter(d => d.timeSeriesIndex >= filterRange[0] && d.timeSeriesIndex <= filterRange[1]) : data;
    return d3.quadtree<ProjectedPoint>()
        .x(d => d.coords[0])
        .y(d => d.coords[1])
        .addAll(filteredData);
}