<script lang="ts">
    import {onMount} from "svelte";
    import {type Annotation, type ChartColors, type ProjectedPoint, ProjectionMode} from "@lib/types";
    import {
        chartSettings,
        defaultChartSettings,
        filterRangeIndexed,
        filterRangePercent,
        hoverPoint,
        hoverRange,
        selectedProjectedPoints
    } from "@lib/stores";
    import ChartSettings from "@components/detail-view/ChartSettings.svelte";
    import {computeColors} from "@lib/chartLogic/chartColors";
    import NavigatorChart from "@components/detail-view/NavigatorChart.svelte";
    import AnnotatorChart from "@components/detail-view/AnnotatorChart.svelte";
    import ScatterPlot from "@components/detail-view/ScatterPlot.svelte";
    import ColorLegend from "@components/atoms/ColorLegend.svelte";

    export let dataset: string;
    export let subset: string;
    export let chunk: string;
    export let timeSeries: number[] = [];
    export let projected: number[][] = [];
    export let normalTube: [number, number] = [0, 0];
    export let similarities: number[] = [];
    export let freq: number[] = [];
    export let mdsEmbedding: number[][] = [];
    export let labels: Annotation[] = [];
    export let events: number[] = [];

    let offset: number = timeSeries.length - projected.length;

    let projectedIndexed: ProjectedPoint[] = [];
    let colors: ChartColors;

    const indexProjectedPoints = (data: number[][]) => {
        projectedIndexed = data.map((d, i): ProjectedPoint => ({
            projectedIndex: i,
            timeSeriesIndex: i + Math.floor(offset / 2),
            coords: d
        }));
        return projectedIndexed
    }


    const reset = () => {
        filterRangeIndexed.set(null)
        filterRangePercent.set(null)
        chartSettings.set(defaultChartSettings)
        hoverPoint.set(undefined)
        hoverRange.set(undefined)
        selectedProjectedPoints.set([])
    }

    const dataUpdate = (do_reset: boolean) => {
        if (do_reset) reset();
        const projectionData = $chartSettings.projection === ProjectionMode.Paths ? projected : mdsEmbedding
        offset = timeSeries.length - projected.length;
        colors = computeColors($chartSettings.color, projectionData, similarities, freq, normalTube, offset)
        indexProjectedPoints(projectionData)
    }

    chartSettings.subscribe(() => dataUpdate(false))

    onMount(() => dataUpdate(true))

    $: mdsEmbedding, dataUpdate(false)
</script>

<div class="fixed top-3 right-3 z-10">
    <ChartSettings/>
</div>
<NavigatorChart timeSeries={timeSeries} labels={labels} events={events} colors={colors.tsColors}/>
<AnnotatorChart
        timeSeries={timeSeries} projected={projectedIndexed} labels={labels}
        subset={subset} chunk={chunk} events={events} dataset={dataset}
        colors={colors.tsColors}
/>
{#if $chartSettings.projection === ProjectionMode.Paths}
    <ScatterPlot
            dataset={dataset} subset={subset} chunk={chunk} timeSeries={timeSeries}
            projected={indexProjectedPoints(projected)}
            colors={colors.projectedColors}
    />
{:else}
    {#key mdsEmbedding}
        <ScatterPlot
                dataset={dataset} subset={subset} chunk={chunk} timeSeries={timeSeries}
                projected={indexProjectedPoints(mdsEmbedding)}
                colors={colors.projectedColors}
        />
    {/key}
{/if}
<div class="fixed bottom-5 right-5 z-10 w-[500px] p-5 shadow-lg bg-white">
    <ColorLegend colorMode={$chartSettings.color}/>
</div>