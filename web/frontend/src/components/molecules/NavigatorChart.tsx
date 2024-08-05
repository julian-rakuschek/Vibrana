import {forwardRef, useEffect, useImperativeHandle, useMemo, useRef} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";

const NavigatorChart = forwardRef(({chartId, data, width, height, onBrush}: {
    chartId: string;
    data: number[];
    width?: number;
    height?: number;
    onBrush?: (range: number[]) => void;
}, ref) => {
    const id = chartId === undefined ? "line" : chartId;
    const transformed = useMemo(() => data.map((d, index) => {
        return {x: index, y: d}
    }), [chartId])
    const min_value = useMemo(() => Math.min(...data), [chartId])
    const max_value = useMemo(() => Math.max(...data), [chartId])
    const xScale = d3.scaleLinear().domain([0, data.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);
    const brushedRange = useRef<[number, number] | null>(null)

    const pointSeries = fc.seriesWebglLine().crossValue(d => d.x).mainValue(d => d.y);

    const brush = fc.brushX().on('brush', e => {
        if (e.selection) {
            brushedRange.current = e.selection;
            if (onBrush) onBrush(e.selection)
            render();
        }
    });

    const chart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(
            fc
                .seriesWebglMulti()
                .series([pointSeries])
        )
        .svgPlotArea(
            fc.seriesSvgMulti()
                .series([brush])
                .mapping(() => brushedRange)
        );

    const render = () => {
        d3.select(`#${id}`).datum(transformed).call(chart)
    };
    useEffect(() => {
        render()
    }, [data.length, chartId]);

    useImperativeHandle(ref, () => ({
        getBrushedRange: () => brushedRange.current
    }));

    return (
        <div
            id={id}
            style={{
                width: width != undefined ? width : "100%",
                height: height != undefined ? height : "95vh"
            }}
        ></div>
    );
});

export default NavigatorChart;