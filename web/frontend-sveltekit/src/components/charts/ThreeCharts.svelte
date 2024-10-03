<script lang="ts">
    import NavigatorChart from "./NavigatorChart.svelte";
    import {onMount} from "svelte";
    import {type Label, type ProjectedPoint} from "@lib/types";
    // import AnnotatorChart from "./AnnotatorChart.svelte";
    // import ScatterPlot from "./ScatterPlot.svelte";
    import {chartSettings, defaultChartSettings, filterRangeIndexed, filterRangePercent, hoverPoint, hoverRange, selectedProjectedPoints} from "@lib/stores";
    import ChartSettings from "./ChartSettings.svelte";
    import {computeColors} from "@lib/chartLogic/chartColors";
    import AnnotatorChart from "@components/charts/AnnotatorChart.svelte";
    import ScatterPlot from "@components/charts/ScatterPlot.svelte";

    export let timeSeries: number[] = [];
    export let projected: number[][] = [];
    export let normalTube: [number, number] = [0, 0];
    export let similarities: number[] = [];
    export let mdsEmbedding: number[][] = [];
    export let labels: Label[] = [];
    export let events: number[] = [];

    const offset: number = timeSeries.length - projected.length;
    let projectedIndexed: ProjectedPoint[] = projected.map((d, i): ProjectedPoint => ({
        projectedIndex: i,
        timeSeriesIndex: i + offset,
        coords: d
    }));

    const reset = () => {
        filterRangeIndexed.set(null)
        filterRangePercent.set(null)
        chartSettings.set(defaultChartSettings)
        hoverPoint.set(undefined)
        hoverRange.set(undefined)
        selectedProjectedPoints.set([])
    }

    chartSettings.subscribe(() => {
        computeColors($chartSettings, projected, similarities, normalTube, offset)
    })

    onMount(() => {
        reset()
        computeColors($chartSettings, projected, similarities, normalTube, offset)
    })
</script>

<button on:click={() => reset()}>Reset</button>

<div class="fixed top-3 right-3 z-10">
    <ChartSettings />
</div>
<NavigatorChart timeSeries={timeSeries} projected={projectedIndexed} labels={labels} events={events} />
<AnnotatorChart timeSeries={timeSeries} projected={projectedIndexed} labels={labels} events={events} />
<ScatterPlot timeSeries={timeSeries} projected={projectedIndexed} mdsEmbedding={mdsEmbedding} />
