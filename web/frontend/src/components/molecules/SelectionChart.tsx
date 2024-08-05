import {forwardRef, useEffect, useImperativeHandle, useMemo} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";

const SelectionChart = forwardRef(({chartId, data, width, height}: {
    chartId: string;
    data: number[];
    width?: number;
    height?: number
}, ref) => {
    const id = chartId === undefined ? "line" : chartId;
    const transformed = useMemo(() => data.map((d, index) => {
        return {x: index, y: d}
    }), [chartId])
    const min_value = useMemo(() => Math.min(...data), [chartId])
    const max_value = useMemo(() => Math.max(...data), [chartId])
    const xScale = d3.scaleLinear().domain([0, data.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);
    const pointSeries = fc.seriesWebglLine().crossValue(d => d.x).mainValue(d => d.y);


    const verticalBand = fc
        .annotationSvgBand()
        .orient('vertical')
        .xScale(xScale)
        .yScale(yScale)
        .decorate(selection  => {
            selection.selectAll('.band').attr('fill', 'rgba(0, 204, 0, 0.1)');
        });

    const chart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(
            fc
                .seriesWebglMulti()
                .series([pointSeries])
                .mapping(d => d.data)
        )
        .svgPlotArea(
            fc.seriesSvgMulti()
                .series([verticalBand])
                .mapping(d => [d.selected])
        );

    const render = () => {
        d3.select(`#${id}`).datum({data: transformed, selected: {from: 10000, to: 30000}}).call(chart)
    };
    useEffect(() => {
        render()
    }, [data.length, chartId]);

    useImperativeHandle(ref, () => ({
        setRange: (range: number[]) => {
            xScale.domain([data.length * range[0], data.length * range[1]]);
            render();
        }
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

export default SelectionChart;