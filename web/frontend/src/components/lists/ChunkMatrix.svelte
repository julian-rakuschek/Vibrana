<script lang="ts">
    import type {AnomalyMetric, LabelCount} from "@lib/types";
    import {CheckCircle, Icon} from "svelte-hero-icons";
    import ChunkCard from "@components/lists/ChunkCard.svelte";

    export let dataset: string;
    export let subset: string;
    export let chunks: string[];
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let normalTube: [number, number];
    export let labelCounts: LabelCount[];

    let selected_chunk: string | undefined = undefined;

    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }
</script>
<div class="h-full w-full flex flex-col">
    <div class="w-full flex flex-row gap-x-3 grow overflow-hidden">
        <div class="w-2/3 h-full">
            <div class="flex flex-row flex-wrap gap-3 overflow-y-scroll  max-h-full">
                {#each chunks as chunk}
                <button class={`relative flex flex-col rounded-3xl p-2 ${chunk === selected_chunk ? "bg-indigo-500" : "bg-white"} w-40 h-40 transition`}
                        on:click={() => selected_chunk === chunk ? selected_chunk = undefined : selected_chunk = chunk}>
                    {#if normals.indexOf(chunk ?? "") !== -1 }
                        <div class="absolute bottom-5 w-2/3 left-1/2 -translate-x-1/2 flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
                            <Icon src="{CheckCircle}" solid class="w-4 h-4 text-white"/>
                            Anomaly-Free
                        </div>
                    {/if}
                    <img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail"
                         class={`${chunk === selected_chunk ? "rounded-full" : ""} object-scale-down w-40 h-40 bg-white`}/>
                </button>
            {/each}
            </div>
        </div>
        {#if selected_chunk}
            <div class="w-1/3 h-full">
                <ChunkCard
                        dataset={dataset} subset={subset} chunk={selected_chunk}
                        isNormal={normals.indexOf(selected_chunk ?? "") !== -1}
                        anomaly={get_anomaly(selected_chunk, anomaly_ratios)}
                        normalTube={normalTube}
                        labelCount={labelCounts.find(l => l._id === selected_chunk)?.count ?? 0}
                />
            </div>
        {:else}
            <div class="flex flex-col h-full w-1/3 items-center justify-center bg-indigo-50 rounded-3xl p-4 text-indigo-600">
                <p>Click on a point cloud to view its details.</p>
            </div>
        {/if}
    </div>
</div>