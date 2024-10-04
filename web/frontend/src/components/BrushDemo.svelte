<script lang="ts">
    import polygonClipping, {type MultiPolygon, type Pair, type Polygon, type Ring} from "polygon-clipping";
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import {DemoRBush, getCirlcePoints, mousePolygon, polyToTriangles} from "@lib/helper/brushHelper";
    import betterPointer from "@lib/helper/betterPointer";
    import {onMount} from "svelte";

    const xScale = d3.scaleLinear()
    const yScale = d3.scaleLinear()
    
    let trace: number[][] = []
    let poly: MultiPolygon = []
    let triangulation: number[][][] = []
    let lastPoint: Pair | null = null
    let radius = 0.035
    let mouseState: [number, number, number] | null = null
    let selected: Set<number> = new Set()

    const fillColors = ["navy", "lightgreen", "red"]
    const random_scatter: [number, number, number][] = [...Array(1000).keys()].map(i => [Math.random(), Math.random(), i])
    const rtree = new DemoRBush()
    rtree.load(random_scatter)

    function handleBrush(x: number, y: number, button: number) {
        const points: MultiPolygon = [getCirlcePoints([x, y], radius, 20)]
        if (poly === null) poly = points;
        else poly = button === 1 ? polygonClipping.union(poly, points) : polygonClipping.difference(poly, points);
        const scatterPoints = new Set(rtree.find(x, y, radius).map(p => p[2]));
        selected = button === 1 ?
            new Set([...selected, ...scatterPoints]) :
            new Set([...selected].filter(x => !scatterPoints.has(x)));
        if (lastPoint !== null) {
            const distance = Math.sqrt(Math.pow(x - lastPoint[0], 2) + Math.pow(y - lastPoint[1], 2))
            const n_fill_points = Math.floor(distance / (radius / 2));
            const step_vector = [
                (x - lastPoint[0]) / (n_fill_points + 1),
                (y - lastPoint[1]) / (n_fill_points + 1)
            ];
            const current = [...lastPoint]
            for (let i = 0; i < n_fill_points; i++) {
                current[0] += step_vector[0]
                current[1] += step_vector[1]
                const points_fill: MultiPolygon = [getCirlcePoints(current as Pair, radius, 20)]
                poly = button === 1 ? polygonClipping.union(poly, points_fill) : polygonClipping.difference(poly, points_fill)
                const scatterPoints = new Set(rtree.find(current[0], current[1], radius).map(p => p[2]));
                selected = button === 1 ?
                    new Set([...selected, ...scatterPoints]) :
                    new Set([...selected].filter(x => !scatterPoints.has(x)));
            }
        }
        triangulation = poly.map(polyToTriangles).flat(1);
        // triangulation = poly.map(ninja_cut).flat(1);
        lastPoint = [x, y]
    }

    function handleMouseEvent(coord: { x: number; y: number, buttons: number }) {
        if (!coord) {
            lastPoint = null;
            return;
        }
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        mouseState = [x, y, coord.buttons];

        if (coord.buttons === 0) {
            render()
            lastPoint = null;
            return;
        }
        handleBrush(x, y, coord.buttons)
        render();
    }


    const scatterPlot = fc.seriesCanvasPoint().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        // selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
        context.fillStyle = selected.has(index) ? "red" : "gray"
        context.strokeStyle = "transparent";
    });

    const trianglesD3 = fc.seriesCanvasLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        // selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
        context.globalAlpha = 0.2;
        context.fillStyle = datum[0].length === 3 ? fillColors[datum[0][2]] : "gray"
        context.strokeStyle = "transparent";
    });

    const triangulationD3 = fc.seriesCanvasRepeat()
        .xScale(xScale)
        .yScale(yScale)
        .orient("horizontal")
        .series(trianglesD3);

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
        .canvasPlotArea(fc.seriesCanvasMulti().series([scatterPlot, triangulationD3, triangulationMouseD3]).mapping((data, index, series) => {
            switch (series[index]) {
                case scatterPlot:
                    return data.scatter;
                case triangulationD3:
                    return data.triangles;
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
        trace = [];
        poly = [];
        triangulation = [];
        selected = new Set()
        render();
    }

    const render = () => {
        d3.select(`#demo`).datum({
            scatter: random_scatter,
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
    <p>Selected Points: {selected.size}</p>
</div>