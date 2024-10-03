<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import type {Label, Point, ProjectedPoint} from "@lib/types";
    import {onMount} from "svelte";
    import {addAlphaToRGB, webglColor} from "@lib/helper/colorHelper";
    import {filterRangeIndexed, filterRangePercent, selectedProjectedPoints} from "@lib/stores";
    import {selectedToColoredIntervals} from "@lib/helper/util";
    import {colorsTimeSeries} from "@lib/chartLogic/chartColors";

    export let timeSeries: number[];
    export let projected: ProjectedPoint[];
    export let labels: Label[];
    export let events: number[];

    const timeseriesIndexed: Point[] = timeSeries.map((d, index) => ({x: index, y: d}))
    const offset: number = timeSeries.length - projected.length;

    let brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, offset)


    const min_value = Math.min(...timeSeries)
    const max_value = Math.max(...timeSeries)
    const xScale = d3.scaleLinear().domain([0, timeSeries.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    const brushNavigator = fc.brushX().on('brush', (e: { selection: [number, number] | null; }) => {
        if (e.selection) {
            filterRangePercent.set(e.selection);
            filterRangeIndexed.set([e.selection[0] * timeSeries.length, e.selection[1] * timeSeries.length]);
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

    filterRangeIndexed.subscribe(() => render())
    selectedProjectedPoints.subscribe(() => {
        brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, offset);
        render()
    })
    colorsTimeSeries.subscribe(() => {
        brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, offset);
        render()
    })

    onMount(() => {
        render()
    })
</script>

<div id="linechart" style="height: 200px; width: 100%"></div>
