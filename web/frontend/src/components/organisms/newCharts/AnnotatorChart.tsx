import {ReactElement, useEffect, useMemo, useRef} from "react";
import {Label, ThreeChartsSettingsType, TimeSeriesPoint} from "../../../types";
import * as d3 from "d3";
import * as fc from "d3fc";
import {addAlphaToRGB, webglColor} from "lib/colorHelper";
import {atom, useSetAtom} from "jotai";

type props = {
    timeseries: number[];
    labels: Label[];
    settings: ThreeChartsSettingsType;
    chartId: string | number;
    events: number[];
    colors_ts: string[];
    min_value: number;
    max_value: number;
}


export default function AnnotatorChart(
    {
        timeseries,
        labels,
        settings,
        events,
        colors_ts,
        chartId,
        min_value,
        max_value,
    }: props): ReactElement {

    const timeseriesIndexed: TimeSeriesPoint[] = timeseries.map((d, index) => ({
        x: index,
        y: d
    }))

    const xScale = d3.scaleLinear().domain([0, timeseries.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);
    useEffect(() => {
        render()
    }, [timeseries, labels, settings, events]);


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



    const navigatorChart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(fc.seriesSvgMulti().series([]).mapping((data, index, series) => {
        }));

    const render = () => {
        d3.select(`#${chartId}`).datum({
            data: timeseriesIndexed,
        }).call(navigatorChart)
    };

    // render()


    return <div
        id={chartId}
        style={{
            width: "100%",
            height: 200
        }}
    ></div>
}