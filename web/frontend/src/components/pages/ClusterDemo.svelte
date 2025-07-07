<script lang="ts">
    import * as d3 from 'd3';
    import * as fc from 'd3fc';
    import { mousePolygon } from '@lib/helper/brushHelper';
    import betterPointer from '@lib/helper/betterPointer';
    import { onMount } from 'svelte';

    const getRandomNumber = (min: number, max: number) => Math.random() * (max - min) + min;


    const xScale = d3.scaleLinear()
    const yScale = d3.scaleLinear()

    let triangulation: number[][][] = []
    let radius = 0.035
    let mouseState: [number, number, number] | null = null

    let scatter_points: [number, number, number][] = [];

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
        const new_point = [x + Math.cos(random_angle) * random_radius, y + Math.sin(random_angle) * random_radius, scatter_points.length];
        scatter_points = [...scatter_points, new_point];
        render();
    }


    const scatterPlot = fc.seriesCanvasPoint().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        context.fillStyle = "gray"
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

    onMount(() => {
        render()
    })

</script>

<div class="p-10">
    <button on:click={() => reset()}
            class="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center  me-2 mb-2">
        Reset
    </button>
    <div id={"demo"} class="border-gray-700 border-2" style="width: 800px; height: 800px">
    </div>
    <p>Points: {scatter_points.length}</p>
</div>