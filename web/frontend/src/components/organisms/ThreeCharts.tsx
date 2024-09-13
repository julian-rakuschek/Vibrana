import {ReactElement, useEffect, useMemo, useRef, useState} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import betterPointer from "lib/betterPointer"
import {addAlphaToRGB, webglColor} from "lib/colorHelper";
import {
    Annotation, Label,
    ProjectedPoint,
    ProjectionMode,
    ThreeChartsSettingsType,
    TimeSeriesPoint,
    WindowMode
} from "../../types";
import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryClient} from "@tanstack/react-query";
import {PaintBrushIcon, TrashIcon} from "@heroicons/react/24/solid";
import TimeSeriesPathIcon from "components/atoms/TimeSeriesPathIcon";
import {DemoRBush, getCirlcePoints, mousePolygon, polyToTriangles, ProjectedTimeSeriesRBush} from "lib/brushHelper";
import polygonClipping, {MultiPolygon, Pair} from "polygon-clipping";
import {MouseButtonLeft, MouseButtonRight, MouseScroll, VaadinShift} from "components/atoms/MouseKeyboardIcons";
import {mergeIntervals} from "lib/util";
import * as events from "node:events";

type props = {
    timeseries: number[];
    projected: number[][];
    labels: Label[];
    sampleId: string;
    machineId: string;
    settings: ThreeChartsSettingsType;
    key: string | number;
    events: number[];
    colors_ts: string[];
    colors_projected: string[];
}

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
export default function ThreeCharts(
    {
        timeseries,
        projected,
        labels,
        machineId,
        sampleId,
        settings,
        events,
        colors_ts,
        colors_projected,
        key
    }: props): ReactElement {
    const navigatorId = `M${machineId}-${sampleId}-nav`
    const selectorId = `M${machineId}-${sampleId}-sel`
    const windowId = `M${machineId}-${sampleId}-win`
    const projectionId = `M${machineId}-${sampleId}-pro`

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
    // Refs are used instead of React State since they don't trigger a re-render of the component, which is important for fast chart performance
    const filterRangePercent = useRef<[number, number] | null>(null);
    const filterRangeIndexed = useRef<[number, number] | null>(null);
    const hoverRange = useRef<number[] | undefined>(undefined);
    const hoverPoint = useRef<ProjectedPoint | undefined>(undefined);
    const windowSizeRef = useRef<number>(1000);
    const settingsRef = useRef<ThreeChartsSettingsType>(settings);
    const selectorBrushRangeWindowSize = useRef<number[] | undefined>(undefined);
    const modeRef = useRef<string>("add");
    const labelRef = useRef<Annotation[]>(labels);
    const quadtree = useRef(compute_quadtree(projectedIndexed, filterRangeIndexed.current));

    const [mode, setMode] = useState<string>("add")
    const [windowSize, setWindowSize] = useState<number>(1000);
    const [brushActive, setBrushActive] = useState(false)
    const [selectedRadius, setSelectedRadius] = useState(0.03)
    const [timeSeriesPathActive, setTimeSeriesPathActive] = useState(false)
    const timeSeriesPathActiveRef = useRef<boolean>(false)
    const brushActiveRef = useRef<boolean>(false)

    const min_value = useMemo(() => Math.min(...timeseries), [machineId, sampleId, timeseries.length])
    const max_value = useMemo(() => Math.max(...timeseries), [machineId, sampleId, timeseries.length])
    const min_x_value = useMemo(() => Math.min(...projected.map(d => d[0])), [machineId, sampleId, projected.length])
    const max_x_value = useMemo(() => Math.max(...projected.map(d => d[0])), [machineId, sampleId, projected.length])
    const min_y_value = useMemo(() => Math.min(...projected.map(d => d[1])), [machineId, sampleId, projected.length])
    const max_y_value = useMemo(() => Math.max(...projected.map(d => d[1])), [machineId, sampleId, projected.length])
    const radius_colors = useMemo(() => compute_radius_norm(projected), [machineId, sampleId, projected.length]);
    const rtree = new ProjectedTimeSeriesRBush()
    rtree.load(projectedIndexed)

    // Brushing Stuff
    const polyRef = useRef<MultiPolygon>([]);
    const trianRef = useRef<number[][][]>([]);
    const last_point_ref = useRef<Pair | null>(null);
    const radius_ref = useRef<number>(0.03)
    const mouse_state = useRef<[number, number, number] | null>(null)
    const selected_indices = useRef<Set<ProjectedPoint>>(new Set())
    const fillColors = ["navy", "lightgreen", "red"]

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
    }, [timeseries, projected, mode, labels, settings, events]);

    useEffect(() => {
        quadtree.current = compute_quadtree(projectedIndexed, filterRangeIndexed.current)
    }, [projectedIndexed, filterRangeIndexed.current]);

    useEffect(() => {
        timeSeriesPathActiveRef.current = timeSeriesPathActive
        renderAll();
    }, [timeSeriesPathActive]);

    useEffect(() => {
        brushActiveRef.current = brushActive
        renderAll();
    }, [brushActive]);

    useEffect(() => {
        radius_ref.current = selectedRadius
        renderAll();
    }, [selectedRadius]);

    const queryClient = useQueryClient();

    // ----------------------------------------------
    // BRUSHING

    const selectedToColoredIntervals = (selected: ProjectedPoint[]): Annotation[] => {
        const annotations: Annotation[] = selected.map(p => ({
            from: p.timeSeriesIndex - tsIndexOffset,
            to: p.timeSeriesIndex + tsIndexOffset,
            color: radius_colors[p.projectedIndex]
        }))
        const merged = mergeIntervals(annotations)
        return merged
    }

    function handleBrush(x: number, y: number, button: number) {
        const points: MultiPolygon = [getCirlcePoints([x, y], radius_ref.current, 20)]
        if (polyRef.current === null) polyRef.current = points;
        else polyRef.current = button === 1 ? polygonClipping.union(polyRef.current, points) : polygonClipping.difference(polyRef.current, points);
        const scatterPoints = new Set(rtree.find(x, y, radius_ref.current));
        selected_indices.current = button === 1 ?
            new Set([...selected_indices.current, ...scatterPoints]) :
            new Set([...selected_indices.current].filter(x => !scatterPoints.has(x)));
        console.log(selected_indices)
        if (last_point_ref.current !== null) {
            const distance = Math.sqrt(Math.pow(x - last_point_ref.current[0], 2) + Math.pow(y - last_point_ref.current[1], 2))
            const n_fill_points = Math.floor(distance / (radius_ref.current / 2));
            const step_vector = [
                (x - last_point_ref.current[0]) / (n_fill_points + 1),
                (y - last_point_ref.current[1]) / (n_fill_points + 1)
            ];
            const current = [...last_point_ref.current]
            for (let i = 0; i < n_fill_points; i++) {
                current[0] += step_vector[0]
                current[1] += step_vector[1]
                const points_fill: MultiPolygon = [getCirlcePoints(current as Pair, radius_ref.current, 20)]
                polyRef.current = button === 1 ? polygonClipping.union(polyRef.current, points_fill) : polygonClipping.difference(polyRef.current, points_fill)
                const scatterPoints = new Set(rtree.find(current[0], current[1], radius_ref.current));
                selected_indices.current = button === 1 ?
                    new Set([...selected_indices.current, ...scatterPoints]) :
                    new Set([...selected_indices.current].filter(x => !scatterPoints.has(x)));
            }
        }
        trianRef.current = polyRef.current.map(polyToTriangles).flat(1);
        // trianRef.current = polyRef.current.map(ninja_cut).flat(1);
        last_point_ref.current = [x, y]
    }

    const resetBrush = () => {
        polyRef.current = [];
        trianRef.current = [];
        selected_indices.current = new Set()
        renderAll();
    }

    const trianglesD3 = fc.seriesCanvasLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        // selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
        context.globalAlpha = 0.2;
        context.fillStyle = datum[0].length === 3 ? fillColors[datum[0][2]] : "gray"
        context.strokeStyle = "transparent";
    });

    const triangulationD3 = fc.seriesCanvasRepeat()
        .xScale(xScaleProjection)
        .yScale(yScaleProjection)
        .orient("horizontal")
        .series(trianglesD3);

    const triangulationMouseD3 = fc.seriesCanvasRepeat()
        .xScale(xScaleProjection)
        .yScale(yScaleProjection)
        .orient("horizontal")
        .series(trianglesD3);

    // ----------------------------------------------
    // DATA FUNCTIONS

    const timeseriesLine = fc
        .seriesWebglLine()
        .equals((previousData, currentData) => previousData === currentData)
        .crossValue((d: TimeSeriesPoint) => d.x)
        .mainValue((d: TimeSeriesPoint) => d.y)
        .decorate((program) => fc
            .webglStrokeColor()
            .value((d: TimeSeriesPoint) => {
                const col = colors_ts[d.x]
                return webglColor(col, 1)
            })
            .data(timeseriesIndexed)(program));

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
                if (!filterRangeIndexed.current) return webglColor(col, 1)
                return webglColor(
                    d.timeSeriesIndex > filterRangeIndexed.current[0] && d.timeSeriesIndex <= filterRangeIndexed.current[1] ? col : "black",
                    d.timeSeriesIndex > filterRangeIndexed.current[0] && d.timeSeriesIndex <= filterRangeIndexed.current[1] ? 1 : 0.05
                )
            })
            .data(moveMiddleToEnd(projectedIndexed, filterRangeIndexed.current))(program));

    const trace = fc.seriesSvgLine().crossValue(d => d[0]).mainValue(d => d[1])

    const current_dot = fc.annotationSvgCrosshair()
        .x(d => xScaleProjection(d[0]))
        .y(d => yScaleProjection(d[1]))
        .xLabel(() => "")
        .yLabel(() => "")


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

    const resetRange = () => {
        filterRangePercent.current = null;
        filterRangeIndexed.current = null;
        renderAll();
    }

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

        hoverPoint.current = projectedIndexed.find(p => p.timeSeriesIndex === Math.floor(x))

        renderAll();
    }).on("click", async ([coord]: { x: number; y: number }[]) => {
        if (!coord) return;
        const x = xScaleSelector.invert(coord.x);
        const selected = [
            Math.floor(Math.max(0, x - windowSizeRef.current / 2)),
            Math.floor(Math.min(timeseries.length - 1, x + windowSizeRef.current / 2))
        ]
        if (modeRef.current === "add") {
            await ApiRoutes.addLabel.fetch({
                data: {
                    from: selected[0],
                    to: selected[1],
                    sampleId: sampleId,
                    machine: machineId
                }
            })
        }
        if (modeRef.current === "delete") {
            await ApiRoutes.deleteLabelByPos.fetch({params: {pos: Math.floor(x)}})
        }
        await queryClient.invalidateQueries({queryKey: [`/db/labels/${machineId}/${sampleId}`]});
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
    const projectionPointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        if (!coord || !quadtree.current) {
            last_point_ref.current = null;
            return;
        }
        const x = xScaleProjection.invert(coord.x);
        const y = yScaleProjection.invert(coord.y);

        mouse_state.current = [x, y, coord.buttons];
        if (coord.buttons === 0) {
            last_point_ref.current = null;
        } else {
            handleBrush(x, y, coord.buttons)
        }

        const span_width = (Math.abs(max_x_value - min_x_value) + Math.abs(max_y_value - min_y_value)) / 2
        const radius = Math.abs(xScaleProjection.invert(coord.x) - yScaleProjection.invert(coord.x - (span_width * 0.2)));
        const p = quadtree.current.find(x, y, radius);
        hoverPoint.current = p;
        if (p && filterRangeIndexed.current && (p.timeSeriesIndex < filterRangeIndexed.current[0] || p.timeSeriesIndex > filterRangeIndexed.current[1])) {
            hoverRange.current = undefined
        } else {
            if (settingsRef.current.projection === ProjectionMode.Cluster) {
                hoverRange.current = p ? [
                    Math.max(0, Math.floor(p.timeSeriesIndex - windowSizeRef.current / 2)),
                    Math.min(Math.floor(p.timeSeriesIndex + windowSizeRef.current / 2), timeseries.length - 1)
                ] : undefined;
            } else if (settingsRef.current.window === WindowMode.Sliding) {
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
        }).filter(event => {
            return (event.type === "mousedown" && event.shiftKey) || event.type === 'wheel'
        });

    // ----------------------------------------------
    // ANNOTATIONS

    const eventMarkerNavigator = fc
        .annotationSvgLine()
        .orient('vertical')
        .label('')
        .xScale(xScaleNavigator)
        .yScale(yScaleNavigator)
        .decorate(se => {
        se.selectAll('line')
            .style('stroke', 'rgba(255, 0, 0, 0.4)')  // Red color
            .style('stroke-width', '3px');          // Heavier stroke
    });

    const eventMarkerSelector = fc
        .annotationSvgLine()
        .orient('vertical')
        .label('')
        .xScale(xScaleSelector)
        .yScale(yScaleSelector).decorate(se => {
        se.selectAll('line')
            .style('stroke', 'rgba(255, 0, 0, 0.4)')  // Red color
            .style('stroke-width', '3px');          // Heavier stroke
    });

    const savedSelectionAnnotations = fc
        .annotationSvgBand()
        .orient('vertical')
        .xScale(xScaleSelector)
        .yScale(yScaleSelector)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 120, 0, 0.4)');
        });

    const brushedSelectionAnnotations = fc
        .annotationSvgBand()
        .orient("vertical")
        .xScale(xScaleSelector)
        .yScale(yScaleSelector)
        .decorate((se, data) => {
            se.selectAll('.band').attr('fill', (d, i) => {
                const value = d.color || data[i].color;
                return addAlphaToRGB(d3.interpolateTurbo(value), 0.5)
            });
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
        .svgPlotArea(fc.seriesSvgMulti().series([savedSelectionAnnotations, brushNavigator, brushedSelectionAnnotations, eventMarkerNavigator]).mapping((data, index, series) => {
            switch (series[index]) {
                case savedSelectionAnnotations:
                    return data.selected;
                case brushNavigator:
                    return filterRangePercent.current;
                case brushedSelectionAnnotations:
                    return data.brushed;
                case eventMarkerNavigator:
                    return data.events
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
                .series([savedSelectionAnnotations, selectorHoverBand, brushedSelectionAnnotations, eventMarkerSelector])
                .mapping((data, index, series) => {
                    switch (series[index]) {
                        case savedSelectionAnnotations:
                            return data.selected;
                        case selectorHoverBand:
                            return data.hover;
                        case brushedSelectionAnnotations:
                            return data.brushed;
                        case eventMarkerSelector:
                            return data.events
                    }
                })
        )
        .decorate(sel => sel.enter().select("d3fc-svg.plot-area").call(selectorPointer));

    const projectionChart = fc
        .chartCartesian(xScaleProjection, yScaleProjection)
        .webglPlotArea(fc.seriesWebglMulti().series([scatterplot]).mapping(d => d.data))
        .canvasPlotArea(fc.seriesCanvasMulti().series([triangulationD3, triangulationMouseD3]).mapping((data, index, series) => {
            switch (series[index]) {
                case triangulationD3:
                    return data.triangles;
                case triangulationMouseD3:
                    return data.mouse;
            }
        }))
        .svgPlotArea(fc.seriesSvgMulti().series([trace, current_dot]).mapping((data, index, series) => {
            switch (series[index]) {
                case trace:
                    return data.trace;
                case current_dot:
                    return data.hoverPoint;
            }
        }))
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
            selected: labelRef.current,
            brushed: selectedToColoredIntervals(Array.from(selected_indices.current)),
            events: events
        }).call(navigatorChart)
    };

    const renderSelector = () => {
        d3.select(`#${selectorId}`).datum({
            data: timeseriesIndexed,
            selected: labelRef.current,
            hover: [{
                from: hoverRange.current ? hoverRange.current[0] : 0,
                to: hoverRange.current ? hoverRange.current[1] : 0
            }],
            brushed: selectedToColoredIntervals(Array.from(selected_indices.current)),
            events: events
        }).call(selectorChart)
    };

    const renderWindowSizeSelector = () => {
        d3.select(`#${windowId}`).datum({
            data: timeseriesIndexed,
            windowSelection: selectorBrushRangeWindowSize.current,
            events: events
        }).call(windowSizeChart)
    };


    const renderProjection = () => {
        d3.select(`#${projectionId}`).datum({
            data: moveMiddleToEnd(projectedIndexed, filterRangeIndexed.current),
            trace: timeSeriesPathActiveRef.current && hoverRange.current && settings.projection === ProjectionMode.Paths ? projectedIndexed.filter(p => p.timeSeriesIndex >= hoverRange.current[0] && p.timeSeriesIndex < hoverRange.current[1]).map(p => p.coords) : [],
            hoverPoint: !brushActiveRef.current && hoverPoint.current ? [hoverPoint.current.coords] : [],
            triangles: brushActiveRef.current ? trianRef.current : [],
            mouse: brushActiveRef.current && mouse_state.current !== null ? mousePolygon(...mouse_state.current, radius_ref.current) : []
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
            <p>
                Click and drag over the time series to select a subset of the data.
                (<span
                className="cursor-default text-indigo-500 border-b-2 border-indigo-500 border-dotted hover:text-indigo-700 hover:border-indigo-700"
                onClick={() => resetRange()}>Reset</span>)
            </p>
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
        {active_charts.projection &&
            <div className="relative rounded-xl shadow-lg text-center w-full flex flex-row justify-center">
                <div
                    id={projectionId}
                    style={{
                        width: 500,
                        height: 500
                    }}
                ></div>
                <div className="flex flex-col justify-start">
                    <div className="flex flex-row flex-nowrap justify-start items-center gap-3">
                        <MouseButtonLeft className="w-5 h-5"/>
                        <span>Brush: Select points</span>
                    </div>
                    <div className="flex flex-row flex-nowrap justify-start items-center gap-3">
                        <MouseButtonRight className="w-5 h-5"/>
                        <span>Brush: Deselect points</span>
                    </div>
                    <div className="flex flex-row flex-nowrap justify-start items-center gap-3">
                        <MouseScroll className="w-5 h-5"/>
                        <span>Zoom</span>
                    </div>
                    <div className="flex flex-row flex-nowrap justify-start items-center gap-3">
                        <div className="flex flex-row flex-nowrap justify-start items-center gap-1">
                            <MouseButtonLeft className="w-5 h-5"/>
                            <span>+</span>
                            <VaadinShift className="w-7 h-5"/>
                        </div>
                        <span>Move point cloud</span>
                    </div>
                </div>
                <div
                    onClick={() => {
                        setTimeSeriesPathActive(!timeSeriesPathActive);
                        setBrushActive(false)
                    }}
                    className={`absolute top-3 left-3 ${timeSeriesPathActive ? 'bg-indigo-700 text-white' : 'bg-white text-black'} w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition hover:shadow-xl`}
                >
                    <TimeSeriesPathIcon className="w-8 h-8" color={timeSeriesPathActive ? "white" : "black"}/>
                </div>
                <div
                    onClick={() => {
                        setTimeSeriesPathActive(false);
                        setBrushActive(!brushActive);
                    }}
                    className={`absolute top-14 left-3 ${brushActive ? 'bg-indigo-700 text-white' : 'bg-white text-black'} w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition hover:shadow-xl`}
                >
                    <PaintBrushIcon className="w-5 h-5"/>
                </div>
                {brushActive && <div className={`absolute top-14 left-14 flex flex-row gap-1`}>
                    <div onClick={() => resetBrush()}
                         className=" w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition hover:shadow-xl hover:text-white hover:bg-red-500">
                        <TrashIcon className="w-5 h-5"/>
                    </div>
                    <div onClick={() => setSelectedRadius(0.01)}
                         className={`w-10 h-10 rounded-full shadow-lg flex justify-center items-center ${selectedRadius === 0.01 ? "bg-indigo-500" : "bg-white"} transition hover:shadow-xl hover:bg-indigo-500 group`}>
                        <div
                            className={`w-3 h-3 rounded-full ${selectedRadius === 0.01 ? "bg-white" : "bg-black/90"} transition group-hover:bg-white`}/>
                    </div>
                    <div onClick={() => setSelectedRadius(0.02)}
                         className={`w-10 h-10 rounded-full shadow-lg flex justify-center items-center ${selectedRadius === 0.02 ? "bg-indigo-500" : "bg-white"} transition hover:shadow-xl hover:bg-indigo-500 group`}>
                        <div
                            className={`w-4 h-4 rounded-full ${selectedRadius === 0.02 ? "bg-white" : "bg-black/90"} transition group-hover:bg-white`}/>
                    </div>
                    <div onClick={() => setSelectedRadius(0.03)}
                         className={`w-10 h-10 rounded-full shadow-lg flex justify-center items-center ${selectedRadius === 0.03 ? "bg-indigo-500" : "bg-white"} transition hover:shadow-xl hover:bg-indigo-500 group`}>
                        <div
                            className={`w-5 h-5 rounded-full ${selectedRadius === 0.03 ? "bg-white" : "bg-black/90"} transition group-hover:bg-white`}/>
                    </div>
                </div>}
            </div>}
    </div>
}