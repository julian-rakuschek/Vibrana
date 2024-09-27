import {ReactElement, useEffect, useMemo} from "react";
import {Label, ProjectedPoint, ProjectionMode, ThreeChartsSettingsType, WindowMode} from "../../../types";
import * as d3 from "d3";
import {mousePolygon, ProjectedTimeSeriesRBush} from "lib/brushHelper";
import * as fc from "d3fc";
import betterPointer from "lib/betterPointer";
import {webglColor} from "lib/colorHelper";

type props = {
    projected: number[][];
    labels: Label[];
    settings: ThreeChartsSettingsType;
    chartId: string;
    events: number[];
    colors_projected: string[];
    tsIndexOffset: number;
}

const projectionPadding = 0.1;

const compute_radius_norm = (data: number[][]): number[] => {
    const radii = data.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
    const max_rad = Math.max(...radii);
    return radii.map(r => r / max_rad);
}

const compute_quadtree = (data: ProjectedPoint[], filterRange: [number, number] | null): d3.Quadtree<ProjectedPoint> => {
    const filteredData = filterRange ? data.filter(d => d.timeSeriesIndex >= filterRange[0] && d.timeSeriesIndex <= filterRange[1]) : data;
    return d3.quadtree<ProjectedPoint>()
        .x(d => d.coords[0])
        .y(d => d.coords[1])
        .addAll(filteredData);
}

const moveMiddleToEnd = (data: ProjectedPoint[], range: number[] | null): ProjectedPoint[] => {
    if (range === null) return data;
    const [start, end] = range;
    const middlePart = data.slice(start, end);
    return data.slice(0, start).concat(data.slice(end), middlePart);
}

const reducedCloud = (data: ProjectedPoint[], rtree: ProjectedTimeSeriesRBush, bound: {
    min_x: number,
    min_y: number;
    max_x: number;
    max_y: number
}): ProjectedPoint[] => {
    const average = (arr: number[]) => arr.reduce((p, c) => p + c, 0) / arr.length;

    const span_x = bound.max_x - bound.min_x
    const span_y = bound.max_y - bound.min_y
    const step_x = span_x / 100;
    const step_y = span_y / 100;

    const final_points: ProjectedPoint[] = [];
    for (let x = bound.min_x; x < bound.max_x; x += step_x) {
        for (let y = bound.min_y; y < bound.max_y; y += step_y) {
            const points = rtree.findBox(x, x + step_x, y, y + step_y)
            if(points.length === 0) continue;
            const coords = points.map(p => p.coords)
            const avg_x = average(coords.map(c => c[0]))
            const avg_y = average(coords.map(c => c[1]))
            final_points.push({
                projectedIndex: points[0].projectedIndex,
                timeSeriesIndex: points[0].timeSeriesIndex,
                coords: [avg_x, avg_y]
            })
        }
    }
    return final_points;
}

export default function ScatterChart({
                                         projected,
                                         labels,
                                         settings,
                                         events,
                                         colors_projected,
                                         chartId,
                                         tsIndexOffset
                                     }: props): ReactElement {
    const projectedIndexed = projected.map((d, i): ProjectedPoint => ({
        projectedIndex: i,
        timeSeriesIndex: i + tsIndexOffset,
        coords: d
    }))
    const min_x_value = useMemo(() => Math.min(...projected.map(d => d[0])), [projected])
    const max_x_value = useMemo(() => Math.max(...projected.map(d => d[0])), [projected])
    const min_y_value = useMemo(() => Math.min(...projected.map(d => d[1])), [projected])
    const max_y_value = useMemo(() => Math.max(...projected.map(d => d[1])), [projected])
    const radius_colors = useMemo(() => compute_radius_norm(projected), [projected]);
    const rtree = new ProjectedTimeSeriesRBush()
    rtree.load(projectedIndexed)
    const res = useMemo(() => reducedCloud(projectedIndexed, rtree, {
        min_x: min_x_value,
        min_y: min_y_value,
        max_x: max_x_value,
        max_y: max_y_value
    }), [projectedIndexed])
    console.log(res)
    useEffect(() => {
        render()
    }, [projected, colors_projected]);

    const xScaleProjection = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * projectionPadding, max_x_value + Math.abs(min_x_value - max_x_value) * projectionPadding])
        .range([0, 1]);
    const yScaleProjection = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * projectionPadding, max_y_value + Math.abs(min_y_value - max_y_value) * projectionPadding])
        .range([0, 1])

    const xScaleProjectionOriginal = xScaleProjection.copy();
    const yScaleProjectionOriginal = yScaleProjection.copy();

    const scatterplot = fc
        .seriesWebglPoint()
        .equals((previousData, currentData) => previousData === currentData)
        .size(5)
        .crossValue((d: ProjectedPoint) => d.coords[0])
        .mainValue((d: ProjectedPoint) => d.coords[1])
        .decorate((program) => fc
            .webglFillColor()
            .value((d: ProjectedPoint) => {
                const col = colors_projected[d.projectedIndex]
                return webglColor(
                    col,
                    1
                )
            })
            .data(projectedIndexed)(program));


    const projectionPointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        console.log(coord)
    });

    const projectionZoom = d3
        .zoom()
        .on("zoom", (event) => {
            xScaleProjection.domain(event.transform.rescaleX(xScaleProjectionOriginal).domain());
            yScaleProjection.domain(event.transform.rescaleY(yScaleProjectionOriginal).domain());
            render();
        }).filter(event => {
            return (event.type === "mousedown" && event.shiftKey) || event.type === 'wheel'
        });

    const projectionChart = fc
        .chartCartesian(xScaleProjection, yScaleProjection)
        .webglPlotArea(fc.seriesWebglMulti().series([scatterplot]).mapping(d => d.data))
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-webgl.plot-area")
                .on("measure.range", (event) => {
                    xScaleProjectionOriginal.range([0, event.detail.width]);
                    yScaleProjectionOriginal.range([event.detail.height, 0]);
                })
                .call(projectionZoom)
                .call(projectionPointer)
        );


    const render = () => {
        d3.select(`#${chartId}`).datum({
            data: res,
        }).call(projectionChart)
    };

    return <div
        id={chartId}
        style={{
            width: 500,
            height: 500
        }}
    ></div>
}