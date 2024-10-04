<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import type {Point} from "@lib/types";
    import {onMount} from "svelte";
    import {webglColor} from "@lib/helper/colorHelper";
    import {chartSettings, filterRangeIndexed} from "@lib/stores";
    import {colorsTimeSeries} from "@lib/chartLogic/chartColors";

    export let timeSeries: number[];
    const timeseriesIndexed: Point[] = timeSeries.map((d, index) => ({x: index, y: d}))
    export let window: [number, number] = [
        (timeSeries.length / 2 - $chartSettings.windowSize / 2) / timeSeries.length,
        (timeSeries.length / 2 + $chartSettings.windowSize / 2) / timeSeries.length,
    ]
    const min_value = Math.min(...timeSeries)
    const max_value = Math.max(...timeSeries)
    const xScale = d3.scaleLinear().domain([0, timeSeries.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    const brushNavigator = fc.brushX().on('brush', (e: { selection: [number, number] | null; }) => {
        if (e.selection) {
            window = e.selection
            render();
        }
    });

    const timeseriesLine = fc
        .seriesWebglLine()
        .equals((previousData, currentData) => previousData === currentData)
        .crossValue((d: Point) => d.x)
        .mainValue((d: Point) => d.y)
        .decorate((program) => fc
            .webglStrokeColor()
            .value((d: Point) => {
                const col = $colorsTimeSeries[d.x].color
                return webglColor(col, 1)
            })
            .data(timeseriesIndexed)(program));


    const navigatorChart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(fc.seriesSvgMulti().series([brushNavigator]).mapping((data, index, series) => {
            switch (series[index]) {
                case brushNavigator:
                    return data.window;
            }
        }));

    const render = () => {
        d3.select(`#windowSelect`).datum({
            data: timeseriesIndexed,
            window: window
        }).call(navigatorChart)
    };

    filterRangeIndexed.subscribe(() => render())
    colorsTimeSeries.subscribe(() => {
        render()
    })

    onMount(() => {
        render()
    })
</script>

<div id="windowSelect" style="height: 200px; width: 100%"></div>
