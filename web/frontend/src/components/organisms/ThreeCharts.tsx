import {ReactElement, useEffect, useMemo, useRef, useState} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import betterPointer from "lib/betterPointer"
import {webglColor} from "lib/colorHelper";
import {Annotation, ThreeChartsSettingsType, WindowMode} from "../../types";
import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryClient} from "@tanstack/react-query";

type props = {
    timeseries: number[];
    projected: number[][];
    labels: Annotation[];
    sampleId: string;
    machineId: string;
    settings: ThreeChartsSettingsType;
}

type TimeSeriesPoint = {
    x: number;
    y: number;
}

type ProjectedPoint = {
    timeSeriesIndex: number;
    projectedIndex: number;
    coords: number[]
};

const projectionPadding = 0.1;

const active_charts: { [chart: string]: boolean } = {
    navigator: true,
    selector: true,
    projection: true
}

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

/*
 * Yes I know, this component is far too large and violates the React phiolosophy, BUT:
 * When having all charts in one component, it makes data exchange much faster.
 * This is because I need to use Refs since I want to avoid component re-renders at all cost.
 * There is no need to pass states between components via function calls and stuff when using one single component.
 * Therefore this approach is a necessary evil.
 */
export default function ThreeCharts({
                                        timeseries,
                                        projected,
                                        labels,
                                        machineId,
                                        sampleId,
                                        settings
                                    }: props): ReactElement {
    const navigatorId = `${machineId}-${sampleId}-nav`
    const selectorId = `${machineId}-${sampleId}-sel`
    const windowId = `${machineId}-${sampleId}-win`
    const projectionId = `${machineId}-${sampleId}-pro`

    // values that only need to be computed once
    const timeseriesIndexed: TimeSeriesPoint[] = useMemo(() => timeseries.map((d, index) => ({
        x: index,
        y: d
    })), [machineId, sampleId, timeseries.length])
    const projectedIndexed: ProjectedPoint[] = useMemo(() => projected.map((d, i): ProjectedPoint => ({
        projectedIndex: i,
        timeSeriesIndex: i + Math.floor((timeseries.length - projected.length) / 2),
        coords: d
    })), [machineId, sampleId, projected.length, timeseries.length]);
    // Refs are used instead of React State since they don't trigger a re-render of the component, which is important for fast chart performance
    const filterRangePercent = useRef<[number, number] | null>(null);
    const filterRangeIndexed = useRef<[number, number] | null>(null);
    const hoverRange = useRef<number[] | undefined>(undefined);
    const windowSizeRef = useRef<number>(1000);
    const settingsRef = useRef<ThreeChartsSettingsType>(settings);
    const selectorBrushRangeWindowSize = useRef<number[] | undefined>(undefined);
    const modeRef = useRef<string>("add");
    const labelRef = useRef<Annotation[]>(labels);
    const quadtree = useRef(compute_quadtree(projectedIndexed, filterRangeIndexed.current));

    const [mode, setMode] = useState<string>("add")
    const [windowSize, setWindowSize] = useState<number>(1000);

    const min_value = useMemo(() => Math.min(...timeseries), [machineId, sampleId, timeseries.length])
    const max_value = useMemo(() => Math.max(...timeseries), [machineId, sampleId, timeseries.length])
    const min_x_value = useMemo(() => Math.min(...projected.map(d => d[0])), [machineId, sampleId, projected.length])
    const max_x_value = useMemo(() => Math.max(...projected.map(d => d[0])), [machineId, sampleId, projected.length])
    const min_y_value = useMemo(() => Math.min(...projected.map(d => d[1])), [machineId, sampleId, projected.length])
    const max_y_value = useMemo(() => Math.max(...projected.map(d => d[1])), [machineId, sampleId, projected.length])
    const radius_colors = useMemo(() => compute_radius_norm(projected), [machineId, sampleId, projected.length]);


    // All Scales for the plots
    const xScaleNavigator = d3.scaleLinear().domain([0, timeseries.length]).range([0, 1]);
    const yScaleNavigator = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);
    const xScaleSelector = d3.scaleLinear().domain([0, timeseries.length]).range([0, 1]);
    const yScaleSelector = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);
    const xScaleProjection = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * projectionPadding, max_x_value + Math.abs(min_x_value - max_x_value) * projectionPadding])
        .range([0, 1]);
    const yScaleProjection = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * projectionPadding, max_y_value + Math.abs(min_y_value - max_y_value) * projectionPadding])
        .range([0, 1])

    const xScaleProjectionOriginal = xScaleProjection.copy();
    const yScaleProjectionOriginal = yScaleProjection.copy();

    useEffect(() => {
        selectorBrushRangeWindowSize.current = undefined
        modeRef.current = mode
        labelRef.current = labels
        settingsRef.current = settings
        renderAll();
    }, [timeseries.length, projected.length, mode, labels, settings]);

    useEffect(() => {
        quadtree.current = compute_quadtree(projectedIndexed, filterRangeIndexed.current)
    }, [projectedIndexed, filterRangeIndexed.current]);

    const queryClient = useQueryClient();


    // ----------------------------------------------
    // DATA FUNCTIONS

    const timeseriesLine = fc.seriesWebglLine().crossValue((d: TimeSeriesPoint) => d.x).mainValue((d: TimeSeriesPoint) => d.y);

    const scatterplot = fc
        .seriesWebglPoint()
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

    const trace = fc.seriesSvgLine().crossValue(d => d[0]).mainValue(d => d[1])

    // ----------------------------------------------
    // INTERACTION FUNCTIONS

    const brushNavigator = fc.brushX().on('brush', (e: { selection: [number, number] | null; }) => {
        if (e.selection) {
            filterRangePercent.current = e.selection;
            filterRangeIndexed.current = [e.selection[0] * timeseries.length, e.selection[1] * timeseries.length];
            quadtree.current = compute_quadtree(projectedIndexed, filterRangeIndexed.current)
            xScaleSelector.domain(filterRangeIndexed.current);
            renderAll();
        }
    });

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const selectorPointer = betterPointer().on("point", ([coord]: { x: number; y: number }[]) => {
        if (!coord) return;
        const x = xScaleSelector.invert(coord.x);
        if (settingsRef.current.window === WindowMode.Sliding) {
            hoverRange.current = [
                Math.floor(Math.max(0, x - windowSizeRef.current / 2)),
                Math.floor(Math.min(timeseries.length - 1, x + windowSizeRef.current / 2))
            ]
        } else {
            hoverRange.current = [
                Math.floor(Math.max(0, Math.floor(x / windowSizeRef.current) * windowSizeRef.current)),
                Math.floor(Math.min(timeseries.length - 1, Math.ceil(x / windowSizeRef.current) * windowSizeRef.current))
            ]
        }

        renderAll();
    }).on("click", async ([coord]: { x: number; y: number }[]) => {
        if (!coord) return;
        const x = xScaleSelector.invert(coord.x);
        const selected = [
            Math.floor(Math.max(0, x - windowSizeRef.current / 2)),
            Math.floor(Math.min(timeseries.length - 1, x + windowSizeRef.current / 2))
        ]
        if (modeRef.current === "add") {
            await ApiRoutes.addLabel.fetch({data: {from: selected[0], to: selected[1]}, params: {sampleId, machineId}})
        }
        if (modeRef.current === "delete") {
            await ApiRoutes.deleteLabel.fetch({data: {index: x}, params: {sampleId, machineId}})
        }
        await queryClient.invalidateQueries({queryKey: [`/db/${machineId}/labels/${sampleId}`]});
    });

    const selectorBrushWindowSize = fc.brushX().on('brush', (e: { selection: number[] }) => {
        if (e.selection) {
            selectorBrushRangeWindowSize.current = e.selection;
            const range_len = filterRangeIndexed.current ? Math.abs(filterRangeIndexed.current[0] - filterRangeIndexed.current[1]) : timeseries.length;
            windowSizeRef.current = Math.floor(Math.abs(e.selection[0] - e.selection[1]) * range_len);
            setWindowSize(windowSizeRef.current)
            renderAll();
        }
    });

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const projectionPointer = betterPointer().on("point", ([coord]: { x: number; y: number }[]) => {
        if (!coord || !quadtree.current) return;
        const x = xScaleProjection.invert(coord.x);
        const y = yScaleProjection.invert(coord.y);
        const span_width = (Math.abs(max_x_value - min_x_value) + Math.abs(max_y_value - min_y_value)) / 2
        const radius = Math.abs(xScaleProjection.invert(coord.x) - yScaleProjection.invert(coord.x - (span_width * 0.2)));
        const p = quadtree.current.find(x, y, radius);
        if (p && filterRangeIndexed.current && (p.timeSeriesIndex < filterRangeIndexed.current[0] || p.timeSeriesIndex > filterRangeIndexed.current[1])) {
            hoverRange.current = undefined
        } else {
            if (settingsRef.current.window === WindowMode.Sliding) {
                hoverRange.current = p ? [
                    Math.max(0, Math.floor(p.timeSeriesIndex - windowSizeRef.current / 2)),
                    Math.min(Math.floor(p.timeSeriesIndex + windowSizeRef.current / 2), timeseries.length - 1)
                ] : undefined;
            } else {
                hoverRange.current = p ? [
                    Math.floor(Math.max(0, Math.floor(p.timeSeriesIndex / windowSizeRef.current) * windowSizeRef.current)),
                Math.floor(Math.min(timeseries.length - 1, Math.ceil(p.timeSeriesIndex / windowSizeRef.current) * windowSizeRef.current))
                ] : undefined;
            }
        }
        renderAll();
    });

    const projectionZoom = d3
        .zoom()
        .on("zoom", (event) => {
            xScaleProjection.domain(event.transform.rescaleX(xScaleProjectionOriginal).domain());
            yScaleProjection.domain(event.transform.rescaleY(yScaleProjectionOriginal).domain());
            renderAll();
        });

    // ----------------------------------------------
    // ANNOTATIONS

    const savedSelectionAnnotations = fc
        .annotationSvgBand()
        .orient('vertical')
        .xScale(xScaleSelector)
        .yScale(yScaleSelector)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 120, 0, 0.4)');
        });

    const selectorHoverBand = fc
        .annotationSvgBand()
        .orient("vertical")
        .xScale(xScaleSelector)
        .yScale(yScaleSelector)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 204, 0, 0.1)');
        });


    // ----------------------------------------------
    // CHART FUNCTIONS

    const navigatorChart = fc
        .chartCartesian(xScaleNavigator, yScaleNavigator)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(fc.seriesSvgMulti().series([savedSelectionAnnotations, brushNavigator]).mapping((data, index, series) => {
            switch (series[index]) {
                case savedSelectionAnnotations:
                    return data.selected;
                case brushNavigator:
                    return filterRangePercent.current;
            }
        }));

    const windowSizeChart = fc
        .chartCartesian(xScaleSelector, yScaleSelector)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(fc.seriesSvgMulti().series([selectorBrushWindowSize]).mapping(d => d.windowSelection))

    const selectorChart = fc
        .chartCartesian(xScaleSelector, yScaleSelector)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(
            fc.seriesSvgMulti()
                .series([savedSelectionAnnotations, selectorHoverBand])
                .mapping((data, index, series) => {
                    switch (series[index]) {
                        case savedSelectionAnnotations:
                            return data.selected;
                        case selectorHoverBand:
                            return data.hover;
                    }
                })
        )
        .decorate(sel => sel.enter().select("d3fc-svg.plot-area").call(selectorPointer));

    const projectionChart = fc
        .chartCartesian(xScaleProjection, yScaleProjection)
        .webglPlotArea(fc.seriesWebglMulti().series([scatterplot]).mapping(d => d.data))
        .svgPlotArea(fc.seriesSvgMulti().series([trace]).mapping(d => d.trace))
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")
                .on("measure.range", (event) => {
                    xScaleProjectionOriginal.range([0, event.detail.width]);
                    yScaleProjectionOriginal.range([event.detail.height, 0]);
                })
                .call(projectionZoom)
                .call(projectionPointer)
        );

    // ----------------------------------------------
    // RENDER FUNCTIONS
    const renderNavigator = () => {
        d3.select(`#${navigatorId}`).datum({
            data: timeseriesIndexed,
            selected: labelRef.current
        }).call(navigatorChart)
    };

    const renderSelector = () => {
        d3.select(`#${selectorId}`).datum({
            data: timeseriesIndexed,
            selected: labelRef.current,
            hover: [{
                from: hoverRange.current ? hoverRange.current[0] : 0,
                to: hoverRange.current ? hoverRange.current[1] : 0
            }]
        }).call(selectorChart)
    };

    const renderWindowSizeSelector = () => {
        d3.select(`#${windowId}`).datum({
            data: timeseriesIndexed,
            windowSelection: selectorBrushRangeWindowSize.current,
        }).call(windowSizeChart)
    };


    const renderProjection = () => {
        d3.select(`#${projectionId}`).datum({
            data: moveMiddleToEnd(projectedIndexed, filterRangeIndexed.current),
            trace: hoverRange.current ? projectedIndexed.filter(p => p.timeSeriesIndex >= hoverRange.current[0] && p.timeSeriesIndex <= hoverRange.current[1]).map(p => p.coords) : []
        }).call(projectionChart)
    };

    const renderAll = () => {
        renderNavigator();
        renderSelector();
        renderProjection();
        renderWindowSizeSelector();
    }

    // ----------------------------------------------
    // HTML STRUCTURE

    return <div className="flex flex-col gap-4">
        {active_charts.navigator && <div className="rounded-xl shadow-lg text-center">
            <p>Click and drag over the time series to select a subset of the data.</p>
            <div
                id={navigatorId}
                style={{
                    width: "100%",
                    height: 200
                }}
            ></div>
        </div>}
        {active_charts.selector && <div className="rounded-xl shadow-lg text-center flex flex-col items-center">
            <div className="flex flex-row shadow-xl rounded-lg bg-white px-2 py-1 cursor-default">
                <div
                    onClick={() => setMode("add")}
                    className={`${mode === "add" ? 'bg-indigo-700-accent text-white' : 'bg-white text-gray-800/80'} px-3 rounded-lg `}>
                    Draw annotation
                </div>
                <div
                    onClick={() => setMode("delete")}
                    className={`${mode === "delete" ? 'bg-indigo-700-accent text-white' : 'bg-white text-gray-800/80'} px-3 rounded-lg `}>
                    Delete annotation
                </div>
                <div
                    onClick={() => setMode("size")}
                    className={`${mode === "size" ? 'bg-indigo-700-accent text-white ' : 'bg-white text-gray-800/80'} px-3 rounded-lg`}>
                    <span>Select window size ({windowSize})</span>
                </div>
            </div>

            {mode !== "size" && <div
                id={selectorId}
                style={{
                    width: "100%",
                    height: 200
                }}
            ></div>}
            {mode === "size" && <div
                id={windowId}
                style={{
                    width: "100%",
                    height: 200
                }}
            ></div>}
        </div>}
        {active_charts.projection && <div className="rounded-xl shadow-lg text-center">
            <p>Point cloud of the time series. By hovering a point, the path may be inspected and by clicking it, the
                path is saved as a reference window.</p>
            <div
                id={projectionId}
                style={{
                    width: "100%",
                    height: 500
                }}
            ></div>
        </div>}
    </div>
}