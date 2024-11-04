<script lang="ts">
    import type {AnomalyMetric, LabelCount} from "@lib/types";
    import DistanceIndicator from "@components/DistanceIndicator.svelte";
    import Toggle from "@components/atoms/Toggle.svelte";
    import {getContext} from "svelte";
    import {useQueryClient} from "@tanstack/svelte-query";
    import {sessionToggleNormal} from "@lib/helper/sessionStorageHelper";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {CheckCircle, Icon, ArrowTopRightOnSquare} from "svelte-hero-icons";

    export let dataset: string;
    export let subset: string;
    export let chunks: string[];
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let normalTube: [number, number];
    export let labelCounts: LabelCount[];

    let selected_chunk: string | undefined = undefined;
    let selected_chunk_normal: boolean;
    const {ro} = getContext("ro") as { ro: boolean }
    const client = useQueryClient()

    const toggleNormal = async (chunk: string) => {
        if (ro) sessionToggleNormal(dataset, subset)
        else await ApiRoutes.toggleNormal.fetch({params: {dataset, subset, chunk}})
        await client.invalidateQueries();
    }

    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }

    const resetChunk = async (chunk: string) => {
        await ApiRoutes.resetChunk.fetch({params: {dataset, subset, chunk}})
        await client.invalidateQueries();
    }


    $: selected_chunk_normal = normals.indexOf(selected_chunk ?? "") !== -1
</script>

<div class="grid grid-cols-3 place-items-start">
    <div class="flex flex-row flex-wrap mt-5 col-span-2">
        {#each chunks as chunk}
            <button class={`relative flex flex-col rounded-3xl p-2 ${chunk === selected_chunk ? "bg-indigo-500" : "bg-white"} transition`} on:click={() => selected_chunk = chunk}>
                {#if normals.indexOf(chunk ?? "") !== -1 }
                    <div class="absolute bottom-5 w-2/3 left-1/2 -translate-x-1/2 flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
                        <Icon src="{CheckCircle}" solid class="w-4 h-4 text-white"/>
                        Anomaly-Free
                    </div>
                {/if}
                <img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail" class="rounded-full object-scale-down h-40 bg-white"/>
            </button>
        {/each}
    </div>
    {#if selected_chunk}
        <div class="flex flex-col items-center bg-indigo-50 rounded-3xl p-4 gap-4 mt-4 mb-4">
            <a
                    class="flex flex-row gap-1 items-center text-center text-xl font-semibold text-indigo-600 border-dotted border-b-2 border-b-indigo-600 hover:text-indigo-800 hover:border-indigo-800"
                    href={`/datasets/${dataset}/${subset}/${selected_chunk}`}
            >
                {selected_chunk}
                <Icon src="{ArrowTopRightOnSquare}" solid class="w-6 h-6 text-indigo-600"/>
            </a>
            <div class="w-full flex flex-col items-center">
                <div class="grid grid-cols-2">
                    <div>Anomalies</div>
                    <div class="place-self-center">{get_anomaly(selected_chunk, anomaly_ratios)?.count ?? 0}</div>
                    <div>Labels</div>
                    <div class="place-self-center">{labelCounts.find(item => item._id === selected_chunk)?.count ?? 0}</div>
                    <div>Anomaly Free</div>
                    <div class="place-self-center"><Toggle bind:enabled={selected_chunk_normal} onToggle={() => toggleNormal(selected_chunk)}/></div>
                    <div class="col-span-2">
                        <button on:click={() => resetChunk(selected_chunk)} class="w-full rounded-lg px-2 bg-indigo-100 text-indigo-600 text-sm transition hover:bg-red-500 hover:text-white">Reset labels</button>
                    </div>
                </div>
            </div>

            <div class="border-t-[1px] border-solid border-indigo-500 w-full">
                <p class="text-center text-indigo-600 font-semibold">Time Series / Signal</p>
                <img src={`/api/db/${dataset}/${subset}/${selected_chunk}/thumbnail`} alt="thumbnail" class=" object-scale-down w-full"/>
            </div>
            {#if get_anomaly(selected_chunk, anomaly_ratios) !== undefined}
                <div class="border-t-[1px] border-solid border-indigo-500 w-full">
                    <p class="text-center text-indigo-600 font-semibold">Distance Indicator</p>
                    <div class="w-full h-[10px] flex justify-center">
                        <DistanceIndicator distances={get_anomaly(selected_chunk, anomaly_ratios).distances_reduced} normalTube={normalTube} width={380} height={10}/>
                    </div>
                </div>
            {/if}
            <div class="border-t-[1px] border-solid border-indigo-500 w-full">
                <p class="text-center text-indigo-600 font-semibold">Spectrogram</p>
                <img src={`/api/db/${dataset}/${subset}/${selected_chunk}/spectrogram`} alt="thumbnail" class=" object-scale-down w-full"/>
            </div>
            <div class="border-t-[1px] border-solid border-indigo-500 w-full flex flex-col items-center">
                <p class="text-center text-indigo-600 font-semibold">Time Delay Embedding</p>
                <img src={`/api/db/${dataset}/${subset}/${selected_chunk}/projected_thumbnail`} alt="thumbnail" class="object-scale-down w-2/3"/>
            </div>
        </div>
    {/if}
</div>
