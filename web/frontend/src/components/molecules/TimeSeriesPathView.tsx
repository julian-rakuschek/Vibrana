import {forwardRef, ReactElement, useEffect, useImperativeHandle, useMemo, useRef} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import {webglColor} from "lib/colorHelper";

const TimeSeriesPathView = forwardRef(({chartId, data, from_idx, to_idx, width, height, onSelectedPointChange}: {
    chartId: string;
    data: number[][];
    width?: number;
    height?: number;
    from_idx: number;
    to_idx: number;
    onSelectedPointChange?: (selectedPoint: number | undefined) => void;
}, ref) => {

    const id = chartId === undefined ? "scatter" : chartId;
    const padding = 0.1;
    const min_x_value = useMemo(() => Math.min(...data.map(d => d[0])), [chartId])
    const max_x_value = useMemo(() => Math.max(...data.map(d => d[0])), [chartId])
    const min_y_value = useMemo(() => Math.min(...data.map(d => d[1])), [chartId])
    const max_y_value = useMemo(() => Math.max(...data.map(d => d[1])), [chartId])
    const dataWithIndex = data.map((d, i) => ({index: i, coords: d}));
    const quadtree = d3.quadtree<{ index: number; coords: number[] }>()
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
    const selectedPoint = useRef<number | undefined>(undefined);
    const filterRange = useRef<number[] | null>(null);

    useImperativeHandle(ref, () => ({
        getSelectedPoint: () => selectedPoint.current,
        setSelectedPoint: (value: number) => {
            selectedPoint.current = value;
            render();
        },
        setRange: (range: number[]) => {
            filterRange.current = [data.length * range[0], data.length * range[1]];
            render();
        }
    }));

    const pointer = fc.pointer().on("point", ([coord]) => {
        if (!coord || !quadtree) return;
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        const radius = Math.abs(xScale.invert(coord.x) - xScale.invert(coord.x - 20));
        const closestDatum = quadtree.find(x, y, radius);
        selectedPoint.current = closestDatum?.index;
        if (onSelectedPointChange) onSelectedPointChange(selectedPoint.current);
        render();
    });


    const pointSeries = fc
        .seriesWebglPoint()
        .size(20)
        .crossValue(d => d.coords[0])
        .mainValue(d => d.coords[1])
        .decorate((program, _, index) => fc
                .webglFillColor()
                .value((d) => {
                    return webglColor(
                        d.index && d.index > (from_idx * dataWithIndex.length) && d.index <= (to_idx * dataWithIndex.length) ? "blue" : "red",
                        d.index && d.index > (from_idx * dataWithIndex.length) && d.index <= (to_idx * dataWithIndex.length) ? 1 : 0.2
                    )
                })
                .data(dataWithIndex)(program));

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
            data: dataWithIndex,
            trace: selectedPoint.current ? data.slice(selectedPoint.current - 10, selectedPoint.current + 10) : []
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
        // console.log("hi", from_idx)
        render()
    }, [data.length, chartId, from_idx, to_idx]);
    return (
        <div
            id={id}
            style={{
                width: width != undefined ? width : "400px",
                height: height != undefined ? height : "400px"
            }}
        ></div>
    );
});

export default TimeSeriesPathView;