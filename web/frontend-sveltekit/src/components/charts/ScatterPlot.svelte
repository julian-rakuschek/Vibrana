<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import {
        type ProjectedPoint,
        ProjectionMode,
        type ThreeChartsSettingsType,
        type Point, WindowMode
    } from "@lib/types";
    import {onMount} from "svelte";
    import {webglColor} from "@lib/helper/colorHelper";
    import betterPointer from "@lib/helper/betterPointer";
    import {filterRangeIndexed, filterRangePercent, selectedProjectedPoints, hoverPoint, hoverRange, chartSettings} from "@lib/stores";
    import {colorsProjection} from "@lib/chartLogic/chartColors";
    import MouseButtonLeft from "@components/icons/MouseButtonLeft.svelte";
    import MouseButtonRight from "@components/icons/MouseButtonRight.svelte";
    import MouseScroll from "@components/icons/MouseScroll.svelte";
    import VaadinShift from "@components/icons/VaadinShift.svelte";
    import TimeSeriesPathIcon from "@components/icons/TimeSeriesPathIcon.svelte";
    import {Icon, PaintBrush, Trash} from "svelte-hero-icons";
    import SaveIcon from "@components/icons/SaveIcon.svelte";
    import polygonClipping, {type MultiPolygon, type Pair} from "polygon-clipping";
    import {getCirlcePoints, mousePolygon, polyToTriangles, ProjectedTimeSeriesRBush} from "@lib/helper/brushHelper";
    import {compute_quadtree, moveMiddleToEnd} from "@lib/chartLogic/chartUtil";


    export let timeSeries: number[];
    export let projected: ProjectedPoint[];
    export let mdsEmbedding: number[][];


    const projectionPadding = 0.1;
    let timeSeriesPathActive = false;
    let brushActive = false;
    let selectedRadius = 0.02;
    let brushTriangulation: number[][][] = [];
    let brushPolygon: MultiPolygon = [];
    let mouseState: [number, number, number] | null = null;
    let brushLastPoint: Pair | null = null;
    const fillColors = ["navy", "lightgreen", "red"]


    const min_x_value = Math.min(...projected.map(d => d.coords[0]))
    const max_x_value = Math.max(...projected.map(d => d.coords[0]))
    const min_y_value = Math.min(...projected.map(d => d.coords[1]))
    const max_y_value = Math.max(...projected.map(d => d.coords[1]))
    let quadtree = compute_quadtree(projected, $filterRangeIndexed)
    let renderData = moveMiddleToEnd(projected, $filterRangeIndexed)
    const rtree = new ProjectedTimeSeriesRBush()
    rtree.load(projected)

    const xScaleProjection = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * projectionPadding, max_x_value + Math.abs(min_x_value - max_x_value) * projectionPadding])
        .range([0, 1]);
    const yScaleProjection = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * projectionPadding, max_y_value + Math.abs(min_y_value - max_y_value) * projectionPadding])
        .range([0, 1])

    const xScaleProjectionOriginal = xScaleProjection.copy();
    const yScaleProjectionOriginal = yScaleProjection.copy();

    function handleBrush(x: number, y: number, button: number) {
        const points: MultiPolygon = [getCirlcePoints([x, y], selectedRadius, 20)]
        if (brushPolygon === null) brushPolygon = points;
        else brushPolygon = button === 1 ? polygonClipping.union(brushPolygon, points) : polygonClipping.difference(brushPolygon, points);
        const scatterPoints = new Set(rtree.find(x, y, selectedRadius));
        selectedProjectedPoints.update(prev => button === 1 ?
            [...new Set([...prev, ...scatterPoints])] :
            [...new Set([...prev].filter(x => !scatterPoints.has(x)))])
        if (brushLastPoint !== null) {
            const distance = Math.sqrt(Math.pow(x - brushLastPoint[0], 2) + Math.pow(y - brushLastPoint[1], 2))
            const n_fill_points = Math.floor(distance / (selectedRadius / 2));
            const step_vector = [
                (x - brushLastPoint[0]) / (n_fill_points + 1),
                (y - brushLastPoint[1]) / (n_fill_points + 1)
            ];
            const current = [...brushLastPoint]
            for (let i = 0; i < n_fill_points; i++) {
                current[0] += step_vector[0]
                current[1] += step_vector[1]
                const points_fill: MultiPolygon = [getCirlcePoints(current as Pair, selectedRadius, 20)]
                brushPolygon = button === 1 ? polygonClipping.union(brushPolygon, points_fill) : polygonClipping.difference(brushPolygon, points_fill)
                const scatterPoints = new Set(rtree.find(current[0], current[1], selectedRadius));
                selectedProjectedPoints.update(prev => button === 1 ?
                    [...new Set([...prev, ...scatterPoints])] :
                    [...new Set([...prev].filter(x => !scatterPoints.has(x)))])
            }
        }
        brushTriangulation = brushPolygon.map(polyToTriangles).flat(1);
        // trianRef.current = brushPolygon.map(ninja_cut).flat(1);
        brushLastPoint = [x, y]
    }

    const scatterplot = fc
        .seriesWebglPoint()
        .equals((previousData, currentData) => previousData === currentData)
        .size(5)
        .crossValue((d: ProjectedPoint) => d.coords[0])
        .mainValue((d: ProjectedPoint) => d.coords[1])
        .decorate((program) => fc
            .webglFillColor()
            .value((d: ProjectedPoint) => {
                const col = $colorsProjection[d.projectedIndex].color
                if (!$filterRangeIndexed) return webglColor(col, 1)
                return webglColor(
                    d.timeSeriesIndex > $filterRangeIndexed[0] && d.timeSeriesIndex <= $filterRangeIndexed[1] ? col : "black",
                    d.timeSeriesIndex > $filterRangeIndexed[0] && d.timeSeriesIndex <= $filterRangeIndexed[1] ? 1 : 0.05
                )
            })
            .data(renderData)(program));


    const current_dot = fc.annotationSvgCrosshair()
        .x(d => xScaleProjection(d[0]))
        .y(d => yScaleProjection(d[1]))
        .xLabel(() => "")
        .yLabel(() => "")

    const trace = fc.seriesSvgLine().crossValue(d => d[0]).mainValue(d => d[1])

    const trianglesD3 = fc.seriesCanvasLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        // selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
        context.globalAlpha = 0.2;
        context.fillStyle = datum[0].length === 3 ? fillColors[datum[0][2]] : "gray"
        context.strokeStyle = "transparent";
    });

    const triangulationD3 = fc.seriesCanvasRepeat()
        .xScale(xScaleProjection)
        .yScale(yScaleProjection)
        .orient("horizontal")
        .series(trianglesD3);

    const triangulationMouseD3 = fc.seriesCanvasRepeat()
        .xScale(xScaleProjection)
        .yScale(yScaleProjection)
        .orient("horizontal")
        .series(trianglesD3);

    const projectionPointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        if (!coord) {
            brushLastPoint = null;
            return;
        }
        const x = xScaleProjection.invert(coord.x);
        const y = yScaleProjection.invert(coord.y);

        mouseState = [x, y, coord.buttons];
        if (coord.buttons === 0) {
            brushLastPoint = null;
        } else {
            handleBrush(x, y, coord.buttons)
        }

        const span_width = (Math.abs(max_x_value - min_x_value) + Math.abs(max_y_value - min_y_value)) / 2
        const radius = Math.abs(xScaleProjection.invert(coord.x) - yScaleProjection.invert(coord.x - (span_width * 0.2)));
        const p = quadtree.find(x, y, radius);
        hoverPoint.set(p);
        if (p && $filterRangeIndexed && (p.timeSeriesIndex < $filterRangeIndexed[0] || p.timeSeriesIndex > $filterRangeIndexed[1])) {
            hoverRange.set(undefined)
        } else {
            if ($chartSettings.projection === ProjectionMode.Cluster) {
                hoverRange.set(p ? [
                    Math.max(0, Math.floor(p.timeSeriesIndex - $chartSettings.windowSize / 2)),
                    Math.min(Math.floor(p.timeSeriesIndex + $chartSettings.windowSize / 2), timeSeries.length - 1)
                ] : undefined)
            } else if ($chartSettings.window === WindowMode.Sliding) {
                hoverRange.set(p ? [
                    Math.max(0, Math.floor(p.timeSeriesIndex - $chartSettings.windowSize / 2)),
                    Math.min(Math.floor(p.timeSeriesIndex + $chartSettings.windowSize / 2), timeSeries.length - 1)
                ] : undefined)
            } else {
                hoverRange.set(p ? [
                    Math.floor(Math.max(0, Math.floor(p.timeSeriesIndex / $chartSettings.windowSize) * $chartSettings.windowSize)),
                    Math.floor(Math.min(timeSeries.length - 1, Math.ceil(p.timeSeriesIndex / $chartSettings.windowSize) * $chartSettings.windowSize))
                ] : undefined)
            }
        }
        render();
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
        .canvasPlotArea(fc.seriesCanvasMulti().series([triangulationD3, triangulationMouseD3]).mapping((data, index, series) => {
            switch (series[index]) {
                case triangulationD3:
                    return data.triangles;
                case triangulationMouseD3:
                    return data.mouse;
            }
        }))
        .svgPlotArea(fc.seriesSvgMulti().series([trace, current_dot]).mapping((data, index, series) => {
            switch (series[index]) {
                case current_dot:
                    return data.hoverPoint;
                case trace:
                    return data.trace;
            }
        }))
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")
                .on("measure.range", (event) => {
                    xScaleProjectionOriginal.range([0, event.detail.width]);
                    yScaleProjectionOriginal.range([event.detail.height, 0]);
                })
                .call(projectionZoom)
                .call(projectionPointer)
        );


    const render = () => {
        d3.select(`#scatter`).datum({
            data: renderData,
            trace: (timeSeriesPathActive && hoverRange !== undefined && $chartSettings.projection === ProjectionMode.Paths) ? projected.filter(p => p.timeSeriesIndex >= $hoverRange[0] && p.timeSeriesIndex < $hoverRange[1]).map(p => p.coords) : [],
            hoverPoint: !brushActive && $hoverPoint ? [$hoverPoint.coords] : [],
            triangles: brushActive ? brushTriangulation : [],
            mouse: brushActive && mouseState ? mousePolygon(...mouseState, selectedRadius) : []
        }).call(projectionChart)
    };

    const resetBrush = () => {
        brushPolygon = [];
        brushTriangulation = [];
        selectedProjectedPoints.set([])
        render();
    }

    const saveBrushes = () => {

    }

    filterRangeIndexed.subscribe((range) => {
        renderData = moveMiddleToEnd(projected, range)
        quadtree = compute_quadtree(projected, range)
        render()
    })
    hoverRange.subscribe(() => render())
    hoverPoint.subscribe(() => render())
    chartSettings.subscribe(() => render())


    onMount(() => {
        render();
    })

</script>

<div class="relative rounded-xl shadow-lg text-center w-full flex flex-row justify-center">
    <div id="scatter" style="height: 500px; width: 500px"></div>
    <div class="flex flex-col justify-start">
        <div class="flex flex-row flex-nowrap justify-start items-center gap-3">
            <MouseButtonLeft class="w-5 h-5"/>
            <span>Brush: Select points</span>
        </div>
        <div class="flex flex-row flex-nowrap justify-start items-center gap-3">
            <MouseButtonRight class="w-5 h-5"/>
            <span>Brush: Deselect points</span>
        </div>
        <div class="flex flex-row flex-nowrap justify-start items-center gap-3">
            <MouseScroll class="w-5 h-5"/>
            <span>Zoom</span>
        </div>
        <div class="flex flex-row flex-nowrap justify-start items-center gap-3">
            <div class="flex flex-row flex-nowrap justify-start items-center gap-1">
                <MouseButtonLeft class="w-5 h-5"/>
                <span>+</span>
                <VaadinShift class="w-7 h-5"/>
            </div>
            <span>Move point cloud</span>
        </div>
    </div>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div on:click={() => {
        timeSeriesPathActive = !timeSeriesPathActive;
        brushActive = false;
    }}
         class={`absolute top-3 left-3 ${timeSeriesPathActive ? 'bg-indigo-700 text-white' : 'bg-white text-black'} w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition hover:shadow-xl`}>
        <TimeSeriesPathIcon className="w-8 h-8" color={timeSeriesPathActive ? "white" : "black"}/>
    </div>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div on:click={() => {
        timeSeriesPathActive = false;
        brushActive = !brushActive;
    }}
         class={`absolute top-14 left-3 ${brushActive ? 'bg-indigo-700 text-white' : 'bg-white text-black'} w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition hover:shadow-xl`}>
        <Icon src="{PaintBrush}" solid class="w-5 h-5"/>
    </div>
    {#if brushActive}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class={`absolute top-14 left-14 flex flex-row gap-1`}>
            <div on:click={() => resetBrush()}
                 class=" w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition hover:shadow-xl hover:text-white hover:bg-red-500">
                <Icon src="{Trash}" class="w-5 h-5" solid/>
            </div>
            <div on:click={() => selectedRadius = 0.01}
                 class={`w-10 h-10 rounded-full shadow-lg flex justify-center items-center ${selectedRadius === 0.01 ? "bg-indigo-500" : "bg-white"} transition hover:shadow-xl hover:bg-indigo-500 group`}>
                <div
                        class={`w-3 h-3 rounded-full ${selectedRadius === 0.01 ? "bg-white" : "bg-black/90"} transition group-hover:bg-white`}/>
            </div>
            <div on:click={() => selectedRadius = 0.02}
                 class={`w-10 h-10 rounded-full shadow-lg flex justify-center items-center ${selectedRadius === 0.02 ? "bg-indigo-500" : "bg-white"} transition hover:shadow-xl hover:bg-indigo-500 group`}>
                <div
                        class={`w-4 h-4 rounded-full ${selectedRadius === 0.02 ? "bg-white" : "bg-black/90"} transition group-hover:bg-white`}/>
            </div>
            <div on:click={() => selectedRadius = 0.03}
                 class={`w-10 h-10 rounded-full shadow-lg flex justify-center items-center ${selectedRadius === 0.03 ? "bg-indigo-500" : "bg-white"} transition hover:shadow-xl hover:bg-indigo-500 group`}>
                <div
                        class={`w-5 h-5 rounded-full ${selectedRadius === 0.03 ? "bg-white" : "bg-black/90"} transition group-hover:bg-white`}/>
            </div>
            <div on:click={() => saveBrushes()}
                 class=" w-10 h-10 rounded-full shadow-lg flex justify-center items-center transition group hover:shadow-xl hover:text-white hover:bg-green-500">
                <SaveIcon class="w-5 h-5 group-hover:fill-white"/>
            </div>
        </div>
    {/if}
</div>