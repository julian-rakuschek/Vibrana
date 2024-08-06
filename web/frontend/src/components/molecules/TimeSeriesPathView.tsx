import {forwardRef, ReactElement, useEffect, useImperativeHandle, useMemo, useRef} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import {webglColor} from "lib/colorHelper";


type DataIndex = { index: number; coords: number[] };

const compute_radius_norm = (data: number[][]): number[] => {
    const radii = data.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
    const max_rad = Math.max(...radii);
    return radii.map(r => r / max_rad);
}

function moveMiddleToEnd(data: DataIndex[], range: number[] | null): DataIndex[] {
    if (range === null) return data;
    const [start, end] = range;
    const middlePart = data.slice(start, end);
    return data.slice(0, start).concat(data.slice(end), middlePart);
}

const TimeSeriesPathView = forwardRef(({chartId, data, width, height, windowSize, onHoverChange}: {
    chartId: string;
    data: number[][];
    width?: number;
    height?: number;
    windowSize: number;
    onHoverChange?: (range: number[] | undefined) => void;
}, ref) => {
    const id = chartId === undefined ? "scatter" : chartId;
    const padding = 0.1;
    const hoverRange = useRef<number[] | undefined>(undefined);
    const filterRange = useRef<number[] | null>([0, data.length]);
    const min_x_value = useMemo(() => Math.min(...data.map(d => d[0])), [chartId])
    const max_x_value = useMemo(() => Math.max(...data.map(d => d[0])), [chartId])
    const min_y_value = useMemo(() => Math.min(...data.map(d => d[1])), [chartId])
    const max_y_value = useMemo(() => Math.max(...data.map(d => d[1])), [chartId])
    const radius_colors = useMemo(() => compute_radius_norm(data), [chartId]);
    const dataWithIndex: DataIndex[] = data.map((d, i): DataIndex => ({index: i, coords: d}));
    const windowSizeRef = useRef<number>(windowSize)
    const quadtree = d3.quadtree<DataIndex>()
        .x(d => d.coords[0])
        .y(d => d.coords[1])
        .addAll(dataWithIndex);

    const xScale = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * padding, max_x_value + Math.abs(min_x_value - max_x_value) * padding])
        .range([0, 1]);
    const yScale = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * padding, max_y_value + Math.abs(min_y_value - max_y_value) * padding])
        .range([0, 1])

    const xScaleOriginal = xScale.copy();
    const yScaleOriginal = yScale.copy();


    useImperativeHandle(ref, () => ({
        getSelectedPoint: () => hoverRange.current,
        setHoverRange: (range: number[]) => {
            hoverRange.current = range;
            render();
        },
        setRange: (range: number[]) => {
            filterRange.current = range;
            render();
        }
    }));

    const pointer = fc.pointer().on("point", ([coord]) => {
        if (!coord || !quadtree) return;
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        const radius = Math.abs(xScale.invert(coord.x) - xScale.invert(coord.x - 20));
        const closestDatum = quadtree.find(x, y, radius);
        hoverRange.current = closestDatum?.index ? [closestDatum.index, closestDatum.index + windowSizeRef.current] : undefined;
        if (onHoverChange) onHoverChange(hoverRange.current);
        render();
    });


    const pointSeries = fc
        .seriesWebglPoint()
        .size(5)
        .crossValue(d => d.coords[0])
        .mainValue(d => d.coords[1])
        .decorate((program, _, index) => fc
                .webglFillColor()
                .value((d) => {
                    const col = d3.interpolateTurbo(radius_colors[d.index])
                    if (!filterRange.current) return webglColor(col, 0.2)
                    return webglColor(
                        d.index && d.index > filterRange.current[0] && d.index <= filterRange.current[1] ? col : "black",
                        d.index && d.index > filterRange.current[0] && d.index <= filterRange.current[1] ? 1 : 0.05
                    )
                })
                .data(moveMiddleToEnd(dataWithIndex, filterRange.current))(program));

    const trace = fc.seriesSvgLine()
        .crossValue(d => d[0])
        .mainValue(d => d[1])

    const chart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(
            fc
                .seriesWebglMulti()
                .series([pointSeries])
                .mapping(d => d.data)
        )
        .svgPlotArea(
            fc
                .seriesSvgMulti()
                .series([trace])
                .mapping(d => d.trace)
        )
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")
                .on("measure.range", (event) => {
                    xScaleOriginal.range([0, event.detail.width]);
                    yScaleOriginal.range([event.detail.height, 0]);
                })
                .call(zoom)
                .call(pointer)
        );


    const render = () => {
        d3.select(`#${id}`).datum({
            data: moveMiddleToEnd(dataWithIndex, filterRange.current),
            trace: hoverRange.current ? data.slice(hoverRange.current[0], hoverRange.current[1]) : []
        }).call(chart)
    };

    const zoom = d3
        .zoom()
        .on("zoom", (event) => {
            xScale.domain(event.transform.rescaleX(xScaleOriginal).domain());
            yScale.domain(event.transform.rescaleY(yScaleOriginal).domain());
            render();
        });

    useEffect(() => {
        render()
    }, [data, chartId]);

    useEffect(() => {
        windowSizeRef.current = windowSize
    }, [windowSize]);

    return (
        <div className="rounded-xl shadow-lg text-center">
            <p>Point cloud of the time series. By hovering a point, the path may be inspected and by clicking it, the path is saved as a reference window.</p>
            <div
                id={id}
                style={{
                    width: width != undefined ? width : "100%",
                    height: height != undefined ? height : "95vh"
                }}
            ></div>
        </div>
    );
});

export default TimeSeriesPathView;