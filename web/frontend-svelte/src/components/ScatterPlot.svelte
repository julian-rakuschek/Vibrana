<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import type {ProjectedPoint, TimeSeriesPoint} from "../lib/types";
    import {onMount} from "svelte";
    import {webglColor} from "../lib/helper/colorHelper";
    import betterPointer from "../lib/helper/betterPointer";

    export let colors: string[];
    export let projected: number[][];
    export let tsIndexOffset: number;
    const projectionPadding = 0.1;
    const projectedIndexed = projected.map((d, i): ProjectedPoint => ({
        projectedIndex: i,
        timeSeriesIndex: i + tsIndexOffset,
        coords: d
    }))
    const min_x_value = Math.min(...projected.map(d => d[0]))
    const max_x_value = Math.max(...projected.map(d => d[0]))
    const min_y_value = Math.min(...projected.map(d => d[1]))
    const max_y_value = Math.max(...projected.map(d => d[1]))

    const xScaleProjection = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * projectionPadding, max_x_value + Math.abs(min_x_value - max_x_value) * projectionPadding])
        .range([0, 1]);
    const yScaleProjection = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * projectionPadding, max_y_value + Math.abs(min_y_value - max_y_value) * projectionPadding])
        .range([0, 1])

    const xScaleProjectionOriginal = xScaleProjection.copy();
    const yScaleProjectionOriginal = yScaleProjection.copy();

    const scatterplot = fc
        .seriesWebglPoint()
        .equals((previousData, currentData) => previousData === currentData)
        .size(5)
        .crossValue((d: ProjectedPoint) => d.coords[0])
        .mainValue((d: ProjectedPoint) => d.coords[1])
        .decorate((program) => fc
            .webglFillColor()
            .value((d: ProjectedPoint) => {
                const col = colors[d.projectedIndex]
                return webglColor(col, 1)
            })
            .data(projectedIndexed)(program));


    const projectionPointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        console.log(coord)
    });

    const projectionZoom = d3
        .zoom()
        .on("zoom", (event) => {
            xScaleProjection.domain(event.transform.rescaleX(xScaleProjectionOriginal).domain());
            yScaleProjection.domain(event.transform.rescaleY(yScaleProjectionOriginal).domain());
            render();
        }).filter(event => {
            return (event.type === "mousedown" && event.shiftKey) || event.type === 'wheel'
        });

    const projectionChart = fc
        .chartCartesian(xScaleProjection, yScaleProjection)
        .webglPlotArea(fc.seriesWebglMulti().series([scatterplot]).mapping(d => d.data))
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-webgl.plot-area")
                .on("measure.range", (event) => {
                    xScaleProjectionOriginal.range([0, event.detail.width]);
                    yScaleProjectionOriginal.range([event.detail.height, 0]);
                })
                .call(projectionZoom)
                .call(projectionPointer)
        );


    const render = () => {
        d3.select(`#scatter`).datum({
            data: projectedIndexed,
        }).call(projectionChart)
    };

    onMount(() => {
        render();
    })

</script>

<div id="scatter" style="height: 400px; width: 400px"></div>