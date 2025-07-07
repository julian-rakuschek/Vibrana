<script lang="ts">
    import * as d3 from 'd3';
    import * as fc from 'd3fc';
    import {DemoRBush, DummyClusterRBush, mousePolygon} from '@lib/helper/brushHelper';
    import betterPointer from '@lib/helper/betterPointer';
    import { onMount } from 'svelte';
    import {DBSCAN_Scatter} from "@lib/algorithms/incrementalDBSCAN";
    import type {ScatterPoint} from "@lib/types";
    import {createColorsArray} from "@lib/helper/colorHelper";
    import {interpolateTurbo} from "d3";

    const getRandomNumber = (min: number, max: number) => Math.random() * (max - min) + min;


    const xScale = d3.scaleLinear()
    const yScale = d3.scaleLinear()

    let triangulation: number[][][] = []
    let radius = 0.035
    let mouseState: [number, number, number] | null = null

    let scatter_points: ScatterPoint[] = [];
    let cluster_colors: string[] = [];
    let dbscan = new DBSCAN_Scatter(0.1, 3, scatter_points);

    function handleMouseEvent(coord: { x: number; y: number, buttons: number }) {
        if (!coord) {
            return;
        }
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        mouseState = [x, y, coord.buttons];

        if (coord.buttons === 0) {
            render()
            return;
        }
        const random_radius = getRandomNumber(0, radius);
        const random_angle = getRandomNumber(0, 2 * Math.PI);
        const new_point: ScatterPoint = {
            x: x + Math.cos(random_angle) * random_radius,
            y: y + Math.sin(random_angle) * random_radius,
            index: scatter_points.length
        };
        scatter_points = [...scatter_points, new_point];
        dbscan.insert(new_point);
        render();
    }


    const scatterPlot = fc.seriesCanvasPoint().crossValue(d => d.x).mainValue(d => d.y).decorate((context, datum, index) => {
        let color = "lightgray"
        if (index < cluster_colors.length) color = cluster_colors[index];
        context.fillStyle = color
        context.strokeStyle = "transparent";
    });

    const trianglesD3 = fc.seriesCanvasLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        context.globalAlpha = 0.2;
        context.fillStyle = "gray"
        context.strokeStyle = "transparent";
    });

    const triangulationMouseD3 = fc.seriesCanvasRepeat()
        .xScale(xScale)
        .yScale(yScale)
        .orient("horizontal")
        .series(trianglesD3);

    const pointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        handleMouseEvent(coord);
    })

    const chart = fc
        .chartCartesian(xScale, yScale)
        .canvasPlotArea(fc.seriesCanvasMulti().series([scatterPlot, triangulationMouseD3]).mapping((data, index, series) => {
            switch (series[index]) {
                case scatterPlot:
                    return data.scatter;
                case triangulationMouseD3:
                    return data.mouse;
            }
        }))
        .decorate(sel =>
            sel
                .select("d3fc-canvas.plot-area")
                .call(pointer)
        );

    const reset = () => {
        triangulation = [];
        scatter_points = [];
        dbscan = new DBSCAN_Scatter(0.1, 3, scatter_points);
        render();
    }

    const render = () => {
        d3.select(`#demo`).datum({
            scatter: scatter_points,
            polygonOutline: [],
            triangles: triangulation,
            mouse: mouseState !== null ? mousePolygon(...mouseState, radius) : []
        }).call(chart);
    };

    const cluster = () => {
        const cluster_labels = dbscan.cluster()
        const distinct_clusters = Array.from(new Set(cluster_labels.filter(r => r !== -1)));
        let distinct_cluster_colors: string[] = createColorsArray(distinct_clusters.length, { start: 0, end: 1, reverse: false, interpolateFunc: interpolateTurbo })
        cluster_colors = cluster_labels.map(l => l === -1 ? "gray" : distinct_cluster_colors[distinct_clusters.indexOf(l)]);
    };

    onMount(() => {
        render()
    })

</script>

<div class="p-10">
    <button on:click={() => reset()}
            class="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center  me-2 mb-2">
        Reset
    </button>
    <button on:click={() => cluster()}
            class="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center  me-2 mb-2">
        Cluster
    </button>
    <div id={"demo"} class="border-gray-700 border-2" style="width: 800px; height: 800px">
    </div>
    <p>Points: {scatter_points.length}</p>
</div>