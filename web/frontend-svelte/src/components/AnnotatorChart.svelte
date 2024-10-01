<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import type {TimeSeriesPoint} from "../lib/types";
    import {onMount} from "svelte";
    import {webglColor} from "../lib/helper/colorHelper";

    export let values: number[];
    export let colors: string[];
    export let filterRangePercent: null | [number, number] = null
    export let filterRangeIndexed: null | [number, number] = null


    const timeseriesIndexed: TimeSeriesPoint[] = values.map((d, index) => ({
        x: index,
        y: d
    }))

    const min_value = Math.min(...values)
    const max_value = Math.max(...values)
    const xScale = d3.scaleLinear().domain([0, values.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    const timeseriesLine = fc
        .seriesWebglLine()
        .equals((previousData, currentData) => previousData === currentData)
        .crossValue((d: TimeSeriesPoint) => d.x)
        .mainValue((d: TimeSeriesPoint) => d.y)
        .decorate((program) => fc
            .webglStrokeColor()
            .value((d: TimeSeriesPoint) => {
                const col = colors[d.x]
                return webglColor(col, 1)
            })
            .data(timeseriesIndexed)(program));


    const navigatorChart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data));

    const render = () => {
        d3.select(`#annotator`).datum({
            data: timeseriesIndexed,
        }).call(navigatorChart)
    };
    $: {
        xScale.domain(filterRangeIndexed ? filterRangeIndexed : [0, values.length]);
        render()
    }

    onMount(() => {
        render()
    })
</script>

<div id="annotator" style="height: 200px; width: 100%"></div>
