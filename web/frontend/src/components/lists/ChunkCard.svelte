<script lang="ts">
    import {CheckCircle, Icon} from "svelte-hero-icons";
    import type {AnomalyMetric} from "@lib/types";
    import DistanceIndicator from "@components/similarities/DistanceIndicator.svelte";
    import {sessionToggleNormal} from "@lib/helper/sessionStorageHelper";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {getContext} from "svelte";
    import {useQueryClient} from "@tanstack/svelte-query";

    export let isNormal: boolean;
    export let dataset: string;
    export let subset: string;
    export let chunk: string;
    export let anomaly: AnomalyMetric | undefined;
    export let normalTube: [number, number];
    export let labelCount: number;

    const {ro} = getContext("ro") as { ro: boolean }
    const client = useQueryClient()

    const toggleNormal = async () => {
        if (ro) sessionToggleNormal(dataset, subset, chunk)
        else await ApiRoutes.toggleNormal.fetch({params: {dataset, subset, chunk}})
        await client.invalidateQueries();
    }

    const resetChunk = async () => {
        await ApiRoutes.resetChunk.fetch({params: {dataset, subset, chunk}})
        await client.invalidateQueries();
    }

</script>



<a class={`w-full grid grid-cols-4 border-4 border-indigo-700 shadow-xl rounded-xl h-52 p-4 gap-4 relative my-8 transition hover:shadow-2xl hover:border-indigo-900`} href={`/datasets/${dataset}/${subset}/${chunk}`}>
    <div class="grow w-full h-full flex flex-col justify-between border-r-2 px-2 border-indigo-700">
        <div>
            <div class="font-semibold grid grid-cols-2">
                <span>{chunk}</span>
                {#if isNormal }
                    <div class="flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
                        <Icon src="{CheckCircle}" solid class="w-4 h-4 text-white"/>
                        Anomaly-Free
                    </div>
                {/if}
            </div>
            <p>Labels: {labelCount}</p>
            <p>Anomalies: {anomaly?.count ?? 0}</p>
        </div>
        <div class="flex flex-col gap-2">
            <button on:click|preventDefault|stopPropagation={() => toggleNormal()} class="rounded-lg px-2 py-1 bg-indigo-50 text-indigo-600 text-sm transition hover:bg-indigo-500 hover:text-white">
                {isNormal ? "Remove anomaly-free status" : "Mark as anomaly-free"}
            </button>
            <button on:click|preventDefault|stopPropagation={() => resetChunk()} class="rounded-lg px-2 py-1 bg-indigo-50 text-indigo-600 text-sm transition hover:bg-red-500 hover:text-white">Reset labels</button>
        </div>
    </div>
    <div class="flex flex-col h-full w-full">
        <p class="text-center">Time Series / Signal</p>
        <img src={`/api/db/${dataset}/${subset}/${chunk}/thumbnail`} alt="thumbnail" class="object-contain w-full"/>
        {#if anomaly !== undefined}
            <div class="w-full h-[10px] flex justify-center">
                <DistanceIndicator distances={anomaly.distances_reduced} normalTube={normalTube} width={380} height={10}/>
            </div>
        {/if}
    </div>
    <div class="flex flex-col h-full w-full">
        <p class="text-center">Frequencies over Time (Spectrogram)</p>
        <img src={`/api/db/${dataset}/${subset}/${chunk}/spectrogram`} alt="thumbnail" class="object-contain w-full"/>
    </div>
    <div class="flex flex-col h-full w-full">
        <p class="text-center">Time Delay Embedding</p>
        <img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail" class="object-contain h-36 w-full"/>
    </div>
</a>
