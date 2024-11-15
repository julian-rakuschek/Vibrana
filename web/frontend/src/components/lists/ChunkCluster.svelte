<script lang="ts">
    import type {AnomalyMetric, Dendrogram, LabelCount} from "@lib/types";
    import {getClusters, getDValues} from "@lib/helper/dendrogram";
    import {numberClusters} from "@lib/stores";
    import * as d3 from "d3";
    import RangeSlider from "svelte-range-slider-pips";
    import {hexToRGBA} from "@lib/helper/colorHelper";
    import {CheckCircle, Icon} from "svelte-hero-icons";
    import ChunkCard from "@components/lists/ChunkCard.svelte";

    export let clustering: Dendrogram;

    let selected_chunk: string | undefined;

    export let dataset: string;
    export let subset: string;
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let normalTube: [number, number];
    export let labelCounts: LabelCount[];

    const d_vals = getDValues(clustering).sort().reverse();
    let clusters = getClusters(clustering, d_vals[$numberClusters - 1])
    const cluster_colors = d3.scaleSequential(d3.interpolateViridis);

    const getColor = (idx: number, n: number): string => cluster_colors((idx + 0.5) / Math.min(d_vals.length - 1, n));

    numberClusters.subscribe((n) => {
        clusters = getClusters(clustering, d_vals[Math.min(d_vals.length - 1, n - 1)])
    })

    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }
</script>
<div class="h-full w-full flex flex-col">
    <div class="grid grid-cols-4 w-1/3 mx-auto place-items-center z-50">
        <p>Number of clusters:</p>
        <div class="col-span-3 w-full">
            <RangeSlider bind:value={$numberClusters} min={1} max={10} step={1} pips float/>
        </div>
    </div>

    <div class="w-full flex flex-row gap-3 grow overflow-hidden">
        <div class="flex flex-row gap-3 w-2/3 h-full">
            {#each clusters as cluster, idx}
                <div class="flex flex-col h-full overflow-y-scroll w-[200px] border-2 rounded-2xl gap-2 p-2"
                     style={`border-color: ${getColor(idx, $numberClusters)}; background-color: ${hexToRGBA(getColor(idx, $numberClusters), 0.4)};`}>
                    {#each cluster as chunk}
                        <button class={`relative flex flex-col rounded-3xl p-2 ${chunk === selected_chunk ? "bg-indigo-500" : "bg-white"} transition`}
                                on:click={() => selected_chunk === chunk ? selected_chunk = undefined : selected_chunk = chunk}>
                            {#if normals.indexOf(chunk ?? "") !== -1 }
                                <div class="absolute bottom-5 w-2/3 left-1/2 -translate-x-1/2 flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
                                    <Icon src="{CheckCircle}" solid class="w-4 h-4 text-white"/>
                                    Anomaly-Free
                                </div>
                            {/if}
                            <img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail"
                                 class={`${chunk === selected_chunk ? "rounded-full" : ""} object-scale-down w-full bg-white`}/>
                        </button>
                    {/each}
                </div>
            {/each}
        </div>
        {#if selected_chunk}
            <div class="w-1/3 h-full">
                <ChunkCard
                        dataset={dataset} subset={subset} chunk={selected_chunk}
                        isNormal={normals.indexOf(selected_chunk ?? "") !== -1}
                        anomaly={get_anomaly(selected_chunk, anomaly_ratios)}
                        normalTube={normalTube}
                        labelCount={labelCounts.find(l => l._id === selected_chunk)?.count ?? 0}/>
            </div>
        {:else}
            <div class="flex flex-col h-full overflow-y-scroll w-1/3 items-center justify-center bg-indigo-50 rounded-3xl p-4 text-indigo-600">
                <p>Click on a point cloud to view its details.</p>
            </div>
        {/if}
    </div>

</div>
