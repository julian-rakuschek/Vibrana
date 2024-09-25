import {Label, ProjectedPoint, ProjectionMode, ThreeChartsSettingsType, TimeSeriesPoint, WindowMode} from "../../types";
import {ReactElement, useEffect, useMemo, useRef} from "react";
import * as d3 from "d3";
import {mousePolygon} from "lib/brushHelper";
import * as fc from "d3fc";
import betterPointer from "lib/betterPointer";
import {webglColor} from "lib/colorHelper";

type props = {
    timeseries: number[];
    projected: number[][];
    labels: Label[];
    sampleId: string;
    machineId: string;
    settings: ThreeChartsSettingsType;
    key: string | number;
}
const projectionPadding = 0.1;

const moveMiddleToEnd = (data: ProjectedPoint[], range: number[] | null): ProjectedPoint[] => {
    if (range === null) return data;
    const [start, end] = range;
    const middlePart = data.slice(start, end);
    return data.slice(0, start).concat(data.slice(end), middlePart);
}

const compute_radius_norm = (data: number[][]): number[] => {
    const radii = data.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
    const max_rad = Math.max(...radii);
    return radii.map(r => r / max_rad);
}


export default function ThreeChartsOptimized(
    {
        timeseries,
        projected,
        labels,
        machineId,
        sampleId,
        settings,
        key
    }: props): ReactElement {
    const navigatorId = `${machineId}-${sampleId}-nav`
    const selectorId = `${machineId}-${sampleId}-sel`
    const windowId = `${machineId}-${sampleId}-win`
    const projectionId = `${machineId}-${sampleId}-pro`

    const timeseriesIndexed: TimeSeriesPoint[] = timeseries.map((d, index) => ({
        x: index,
        y: d
    }))
    const tsIndexOffset = Math.floor((timeseries.length - projected.length) / 2)
    const projectedIndexed = projected.map((d, i): ProjectedPoint => ({
        projectedIndex: i,
        timeSeriesIndex: i + tsIndexOffset,
        coords: d
    }))
    const radius_colors = useMemo(() => compute_radius_norm(projected), [machineId, sampleId, projected.length]);
    const filterRangePercent = useRef<[number, number] | null>(null);
    const filterRangeIndexed = useRef<[number, number] | null>(null);

    const min_x_value = useMemo(() => Math.min(...projected.map(d => d[0])), [machineId, sampleId, projected.length])
    const max_x_value = useMemo(() => Math.max(...projected.map(d => d[0])), [machineId, sampleId, projected.length])
    const min_y_value = useMemo(() => Math.min(...projected.map(d => d[1])), [machineId, sampleId, projected.length])
    const max_y_value = useMemo(() => Math.max(...projected.map(d => d[1])), [machineId, sampleId, projected.length])
    const xScaleProjection = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * projectionPadding, max_x_value + Math.abs(min_x_value - max_x_value) * projectionPadding])
        .range([0, 1]);
    const yScaleProjection = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * projectionPadding, max_y_value + Math.abs(min_y_value - max_y_value) * projectionPadding])
        .range([0, 1])
    const xScaleProjectionOriginal = xScaleProjection.copy();
    const yScaleProjectionOriginal = yScaleProjection.copy();

    useEffect(() => {
        renderAll();
    }, [timeseries, projected, labels, settings]);

    const optimisedPointSeries = () => {
        let draw = fc
            .glPoint()
            .decorate(program => {
                fc.pointFill().color([1, 0, 0, 1])(program);
                fc.pointAntiAlias()(program);

                const gl = program.context();
                gl.enable(gl.BLEND);
                gl.blendFuncSeparate(
                    gl.SRC_ALPHA,
                    gl.ONE_MINUS_DST_ALPHA,
                    gl.ONE,
                    gl.ONE_MINUS_SRC_ALPHA
                );
            });

        const pointSeries = data => {
            draw.type(fc.circlePointShader());
            draw(data.length);
        };

        pointSeries.xValues = (...args) => {
            draw.xValues(args[0]);
            return pointSeries;
        };
        pointSeries.yValues = (...args) => {
            draw.yValues(args[0]);
            return pointSeries;
        };
        pointSeries.sizes = (...args) => {
            draw.sizes(args[0]);
            return pointSeries;
        };

        pointSeries.context = (...args) => {
            draw.context(args[0]);
            return pointSeries;
        };
        pointSeries.xScale = (...args) => {
            draw.xScale(fc.scaleMapper(args[0]).glScale);
            return pointSeries;
        };
        pointSeries.yScale = (...args) => {
            draw.yScale(fc.scaleMapper(args[0]).glScale);
            return pointSeries;
        };

        return pointSeries;
    };

    const scatterplot2 = optimisedPointSeries()

    const scatterplot = fc
        .seriesWebglPoint()
        .equals((previousData, currentData) => previousData === currentData)
        .size(5)
        .crossValue((d: ProjectedPoint) => d.coords[0])
        .mainValue((d: ProjectedPoint) => d.coords[1])
        .decorate((program) => fc
            .webglFillColor()
            .value((d: ProjectedPoint) => {
                const col = d3.interpolateTurbo(radius_colors[d.projectedIndex])
                if (!filterRangeIndexed.current) return webglColor(col, 1)
                return webglColor(
                    d.timeSeriesIndex > filterRangeIndexed.current[0] && d.timeSeriesIndex <= filterRangeIndexed.current[1] ? col : "black",
                    d.timeSeriesIndex > filterRangeIndexed.current[0] && d.timeSeriesIndex <= filterRangeIndexed.current[1] ? 1 : 0.05
                )
            })
            .data(moveMiddleToEnd(projectedIndexed, filterRangeIndexed.current))(program));

    const projectionPointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        console.log(coord)
        renderAll();
    });

    const projectionZoom = d3
        .zoom()
        .on("zoom", (event) => {
            xScaleProjection.domain(event.transform.rescaleX(xScaleProjectionOriginal).domain());
            yScaleProjection.domain(event.transform.rescaleY(yScaleProjectionOriginal).domain());
            renderAll();
        }).filter(event => {
            return (event.type === "mousedown" && event.shiftKey) || event.type === 'wheel'
        });


    const projectionChart = fc
        .chartCartesian(xScaleProjection, yScaleProjection)
        .webglPlotArea(fc.seriesWebglMulti().series([scatterplot]).mapping(d => d.data))
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-canvas.plot-area")
                .on("measure.range", (event) => {
                    xScaleProjectionOriginal.range([0, event.detail.width]);
                    yScaleProjectionOriginal.range([event.detail.height, 0]);
                })
                .call(projectionZoom)
                .call(projectionPointer)
        );

    const renderProjection = () => {
        d3.select(`#${projectionId}`).datum({
            data: moveMiddleToEnd(projectedIndexed, filterRangeIndexed.current),
        }).call(projectionChart)
    };

    const renderAll = () => {
        renderProjection();
    }

    return <div className="flex flex-col gap-4">
        <div className="relative rounded-xl text-center w-full flex flex-row justify-center">
            <div
                id={projectionId}
                style={{
                    width: 1000,
                    height: 1000
                }}
            ></div>
        </div>
    </div>
}