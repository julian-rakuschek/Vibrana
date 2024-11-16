<script lang="ts">
    import * as d3 from "d3";
    import {interpolateViridis} from "d3";
    import type {Dendrogram, HeatmapTooltip, SelectedChunk} from "@lib/types";
    import {numberClusters, selectedChunk} from "@lib/stores";
    import {getClusters, getDValues, getLeafsWithClusterLabels} from "@lib/helper/dendrogram";

    export let clustering: Dendrogram;
    export let dataset: string;
    export let subset: string;

    let width = 300
    const height = 20
    let tooltip: HeatmapTooltip = {show: false, x: 0, y: 0};

    const d_vals = getDValues(clustering).sort().reverse();
    let clusters = getLeafsWithClusterLabels(clustering, d_vals[$numberClusters - 1])
    const cluster_colors = d3.scaleSequential(d3.interpolateViridis);

    const getColor = (idx: number, n: number): string => cluster_colors((idx + 0.5) / Math.min(d_vals.length - 1, n));

    function showTooltip(event, cluster) {
        tooltip = {
            show: true,
            x: event.pageX,
            y: event.pageY - 90,
            chunk: cluster
        }
    }

    function hideTooltip() {
        tooltip = {show: false, x: 0, y: 0, chunk: ""};
    }

    const isSelected = (chunk: string, global?: SelectedChunk) => {
        if (!global) return false;
        return global.chunk === chunk && global.subset === subset && global.dataset === dataset
    }

    numberClusters.subscribe((n) => {
        clusters = getLeafsWithClusterLabels(clustering, d_vals[Math.min(d_vals.length - 1, n - 1)])
    })

    $: xScale = d3.scaleLinear().range([0, width]).domain([0, clusters.length]);
    $: yScale = d3.scaleLinear().range([0, height]).domain([0, 1])

</script>
<div class="w-full" bind:clientWidth={width}>
    <svg width={width} height={height}>
        <g width={width} height={height}>
            {#each clusters as cluster, idx}
                <rect
                        x={xScale(idx)}
                        y={yScale(0)}
                        width={width / clusters.length}
                        height={height}
                        opacity={1}
                        fill={getColor(cluster[1], $numberClusters)}
                        stroke={tooltip.show && tooltip.chunk === cluster[0] ? "white" : (isSelected(cluster[0], $selectedChunk) ? "red" : "")}
                        stroke-width="4"
                        on:mouseover={(e) => showTooltip(e, cluster[0])}
                        on:mousemove={(e) => showTooltip(e, cluster[0])}
                        on:mouseout={hideTooltip}
                        on:click={() => isSelected(cluster[0], $selectedChunk) ? selectedChunk.set(undefined) : selectedChunk.set({dataset, subset, chunk: cluster[0]})}
                />
            {/each}
        </g>
    </svg>
</div>

{#if tooltip.show}
    <div
        class="absolute pointer-events-none w-20 h-20 -translate-x-1/2 z-50"
        style="top: {tooltip.y}px; left: {tooltip.x}px;">
        <img src={`/api/db/${dataset}/${subset}/${tooltip.chunk}/projected_thumbnail`} alt="thumbnail" class={`rounded-2xl object-scale-down w-40 bg-white`}/>
    </div>
{/if}