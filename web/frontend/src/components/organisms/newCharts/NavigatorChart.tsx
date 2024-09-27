import {forwardRef, ReactElement, useEffect, useImperativeHandle, useMemo, useRef} from "react";
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
}

export const filterRangePercentAtom = atom<[number, number] | null>(null);
export const filterRangeIndexedAtom = atom<[number, number] | null>(null);

const NavigatorChart = forwardRef(({
    timeseries,
    labels,
    settings,
    events,
    colors_ts,
    chartId
}: props, ref): ReactElement => {

    const timeseriesIndexed: TimeSeriesPoint[] = timeseries.map((d, index) => ({
        x: index,
        y: d
    }))
    // const [filterRangePercent, setfilterRangePercent] = useAtom(filterRangePercentAtom);
    const setfilterRangePercent = useSetAtom(filterRangePercentAtom);
    // const [filterRangeIndexed, setfilterRangeIndexed] = useAtom(filterRangeIndexedAtom);
    const filterRangePercent = useRef<[number, number] | null>(null);
    const filterRangeIndexed = useRef<[number, number] | null>(null);
    const min_value = useMemo(() => Math.min(...timeseries), [timeseries.length])
    const max_value = useMemo(() => Math.max(...timeseries), [timeseries.length])
    const xScale = d3.scaleLinear().domain([0, timeseries.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    useEffect(() => {
        render()
    }, [timeseries, labels, settings, events]);


    const brushedSelectionAnnotations = fc
        .annotationSvgBand()
        .orient("vertical")
        .xScale(xScale)
        .yScale(yScale)
        .decorate((se, data) => {
            se.selectAll('.band').attr('fill', (d, i) => {
                const value = d.color || data[i].color;
                return addAlphaToRGB(d3.interpolateTurbo(value), 0.5)
            });
        });

    const brushNavigator = fc.brushX().on('brush', (e: { selection: [number, number] | null; }) => {
        if (e.selection) {
            filterRangePercent.current = e.selection;
            filterRangeIndexed.current = [e.selection[0] * timeseries.length, e.selection[1] * timeseries.length];
            // xScale.domain(filterRangeIndexed.current);
            setfilterRangePercent(e.selection)
            render();
        }
    });

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
        .svgPlotArea(fc.seriesSvgMulti().series([brushNavigator]).mapping((data, index, series) => {
            switch (series[index]) {
                case brushNavigator:
                    return filterRangePercent.current;
            }
        }));

    useImperativeHandle(ref, () => ({
        reset: () => {
            filterRangePercent.current = null;
            filterRangeIndexed.current = null;
            setfilterRangePercent(null);
            render();
        }
    }));

    const render = () => {
        d3.select(`#${chartId}`).datum({
            data: timeseriesIndexed,
            brushed: filterRangePercent
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
});

export default NavigatorChart;