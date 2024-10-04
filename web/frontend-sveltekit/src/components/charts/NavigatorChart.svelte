<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import type {Annotation, Point, ProjectedPoint} from "@lib/types";
    import {onMount} from "svelte";
    import {addAlphaToRGB, webglColor} from "@lib/helper/colorHelper";
    import {filterRangeIndexed, filterRangePercent, selectedProjectedPoints} from "@lib/stores";
    import {selectedToColoredIntervals} from "@lib/helper/util";
    import {colorsTimeSeries} from "@lib/chartLogic/chartColors";

    export let timeSeries: number[];
    export let projected: ProjectedPoint[];
    export let labels: Annotation[];
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

    const savedAnnotations = fc
        .annotationSvgBand()
        .orient('vertical')
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 120, 0, 0.4)');
        });

    const eventMarker = fc
        .annotationSvgLine()
        .orient('vertical')
        .label('')
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
        se.selectAll('line')
            .style('stroke', 'rgba(255, 0, 0, 0.4)')  // Red color
            .style('stroke-width', '3px');          // Heavier stroke
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
        .svgPlotArea(fc.seriesSvgMulti().series([brushNavigator, brushedSelectionAnnotations, eventMarker, savedAnnotations]).mapping((data, index, series) => {
            switch (series[index]) {
                case brushNavigator:
                    return $filterRangePercent;
                case brushedSelectionAnnotations:
                    return data.brushedIntervals;
                case eventMarker:
                    return data.events;
                case savedAnnotations:
                    return data.savedLabels;
            }
        }));

    const render = () => {
        d3.select(`#linechart`).datum({
            data: timeseriesIndexed,
            events: events,
            savedLabels: labels,
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

    const resetRange = () => {
        filterRangeIndexed.set(null)
        filterRangePercent.set(null)
    }

    onMount(() => {
        render()
    })
</script>

<p class="text-center mt-5"><span class="font-semibold">Navigator</span>: <span class="text-black/70">Select a subset of the signal by dragging an area with the mouse.</span> <button on:click={resetRange} class="cursor-default text-indigo-500 border-b-2 border-indigo-500 border-dotted hover:text-indigo-700 hover:border-indigo-700">Reset Range</button></p>
<div id="linechart" style="height: 200px; width: 100%"></div>
