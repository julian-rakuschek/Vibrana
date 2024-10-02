<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import type {ProjectedPoint, TimeSeriesPoint} from "../lib/types";
    import {onMount} from "svelte";
    import {addAlphaToRGB, webglColor} from "../lib/helper/colorHelper";
    import {filterRangeIndexed, filterRangePercent} from "../lib/stores";
    import {selectedToColoredIntervals} from "../lib/helper/util";

    export let values: number[];
    export let colors: string[];
    export let radius_colors: number[];
    export let hoverPoint: ProjectedPoint | undefined = undefined;
    export let hoverRange: number[] | undefined = undefined;
    const timeseriesIndexed: TimeSeriesPoint[] = values.map((d, index) => ({
        x: index,
        y: d
    }))
    export let selectedIndices: Set<ProjectedPoint> = new Set();
    export let offset: number;

    let brushed = selectedToColoredIntervals(Array.from(selectedIndices), radius_colors, offset)


    const min_value = Math.min(...values)
    const max_value = Math.max(...values)
    const xScale = d3.scaleLinear().domain([0, values.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    const brushNavigator = fc.brushX().on('brush', (e: { selection: [number, number] | null; }) => {
        if (e.selection) {
            filterRangePercent.set(e.selection);
            filterRangeIndexed.set([e.selection[0] * values.length, e.selection[1] * values.length]);
            // xScale.domain(filterRangeIndexed.current);
            render();
        }
    });

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
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(fc.seriesSvgMulti().series([brushNavigator, brushedSelectionAnnotations]).mapping((data, index, series) => {
            switch (series[index]) {
                case brushNavigator:
                    return $filterRangePercent;
                case brushedSelectionAnnotations:
                    return data.brushedIntervals;
            }
        }));

    const render = () => {
        d3.select(`#linechart`).datum({
            data: timeseriesIndexed,
            brushed: $filterRangePercent,
            brushedIntervals: brushed
        }).call(navigatorChart)
    };

    filterRangeIndexed.subscribe((range) => {
        render()
    })

    $: {
        brushed = selectedToColoredIntervals(Array.from(selectedIndices), radius_colors, offset);
        console.log(brushed)
        render()
    }

    onMount(() => {
        render()
    })
</script>

<div id="linechart" style="height: 200px; width: 100%"></div>
