<script lang="ts">
    import NavigatorChart from "./NavigatorChart.svelte";
    import {onMount} from "svelte";
    import {type Annotation, type Label, type ProjectedPoint, ProjectionMode} from "@lib/types";
    // import AnnotatorChart from "./AnnotatorChart.svelte";
    // import ScatterPlot from "./ScatterPlot.svelte";
    import {chartSettings, defaultChartSettings, filterRangeIndexed, filterRangePercent, hoverPoint, hoverRange, selectedProjectedPoints} from "@lib/stores";
    import ChartSettings from "./ChartSettings.svelte";
    import {computeColors} from "@lib/chartLogic/chartColors";
    import AnnotatorChart from "@components/charts/AnnotatorChart.svelte";
    import ScatterPlot from "@components/charts/ScatterPlot.svelte";
    import ColorLegend from "@components/atoms/ColorLegend.svelte";

    export let machineId: string;
    export let sampleId: string;
    export let timeSeries: number[] = [];
    export let projected: number[][] = [];
    export let normalTube: [number, number] = [0, 0];
    export let similarities: number[] = [];
    export let mdsEmbedding: number[][] = [];
    export let labels: Annotation[] = [];
    export let events: number[] = [];

    const offset: number = timeSeries.length - projected.length;
    let projectedIndexed: ProjectedPoint[] = [];
    const indexProjectedPoints = (data: number[][]) => {
        projectedIndexed = data.map((d, i): ProjectedPoint => ({
            projectedIndex: i,
            timeSeriesIndex: i + offset,
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

    chartSettings.subscribe(() => {
        const projectionData = $chartSettings.projection === ProjectionMode.Paths ? projected : mdsEmbedding
        computeColors($chartSettings, projectionData, similarities, normalTube, offset)
        indexProjectedPoints(projectionData)
    })

    onMount(() => {
        reset()
        indexProjectedPoints(projected)
        computeColors($chartSettings, projected, similarities, normalTube, offset)
    })
</script>

<div class="fixed top-3 right-3 z-10">
    <ChartSettings/>
</div>
<NavigatorChart timeSeries={timeSeries} projected={projectedIndexed} labels={labels} events={events}/>
<AnnotatorChart timeSeries={timeSeries} projected={projectedIndexed} labels={labels} events={events} machineId={machineId} sampleId={sampleId} />
{#if $chartSettings.projection === ProjectionMode.Paths}
    <ScatterPlot timeSeries={timeSeries} projected={indexProjectedPoints(projected)}/>
{:else}
    <ScatterPlot timeSeries={timeSeries} projected={indexProjectedPoints(mdsEmbedding)}/>
{/if}
<div class="fixed bottom-5 right-5 z-10 w-[500px] p-5 shadow-lg bg-white">
    <ColorLegend colorMode={$chartSettings.color} />
</div>