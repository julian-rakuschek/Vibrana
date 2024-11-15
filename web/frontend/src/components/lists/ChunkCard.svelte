<script lang="ts">
    import {ArrowTopRightOnSquare, Icon} from "svelte-hero-icons";
    import type {AnomalyMetric} from "@lib/types";
    import DistanceIndicator from "@components/similarities/DistanceIndicator.svelte";
    import {sessionResetChunk, sessionToggleNormal} from "@lib/helper/sessionStorageHelper";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {getContext} from "svelte";
    import {useQueryClient} from "@tanstack/svelte-query";
    import Toggle from "@components/atoms/Toggle.svelte";

    export let dataset: string;
    export let subset: string;
    export let chunk: string;
    export let isNormal: boolean;
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
        if (ro) sessionResetChunk(dataset, subset, chunk)
        else await ApiRoutes.resetChunk.fetch({params: {dataset, subset, chunk}})
        await client.invalidateQueries();
    }

</script>


<div class="flex flex-col items-center bg-indigo-50 rounded-3xl p-4 gap-4 h-full w-full overflow-y-scroll">
    <a
            class="flex flex-row gap-1 items-center text-center text-xl font-semibold text-indigo-600 border-dotted border-b-2 border-b-indigo-600 hover:text-indigo-800 hover:border-indigo-800"
            href={`/datasets/${dataset}/${subset}/${chunk}`}
    >
        {chunk}
        <Icon src="{ArrowTopRightOnSquare}" solid class="w-6 h-6 text-indigo-600"/>
    </a>
    <div class="w-full flex flex-col items-center">
        <div class="grid grid-cols-2">
            <div>Anomalies</div>
            <div class="place-self-center">{anomaly?.count ?? 0}</div>
            <div>Labels</div>
            <div class="place-self-center">{labelCount}</div>
            <div>Anomaly Free</div>
            <div class="place-self-center">
                <Toggle bind:enabled={isNormal} onToggle={() => toggleNormal()}/>
            </div>
            <div class="col-span-2">
                <button on:click={() => resetChunk()}
                        class="w-full rounded-lg px-2 bg-indigo-100 text-indigo-600 text-sm transition hover:bg-red-500 hover:text-white">
                    Reset labels
                </button>
            </div>
        </div>
    </div>

    <div class="border-t-[1px] border-solid border-indigo-500 w-full">
        <p class="text-center text-indigo-600 font-semibold">Time Series / Signal</p>
        <img src={`/api/db/${dataset}/${subset}/${chunk}/thumbnail`} alt="thumbnail"
             class=" object-scale-down w-full"/>
    </div>
    {#if anomaly !== undefined}
        <div class="border-t-[1px] border-solid border-indigo-500 w-full">
            <p class="text-center text-indigo-600 font-semibold">Distance Indicator</p>
            <div class="w-full h-[10px] flex justify-center">
                <DistanceIndicator distances={anomaly.distances_reduced}
                                   normalTube={normalTube} width={380} height={10}/>
            </div>
        </div>
    {/if}
    <div class="border-t-[1px] border-solid border-indigo-500 w-full">
        <p class="text-center text-indigo-600 font-semibold">Spectrogram</p>
        <img src={`/api/db/${dataset}/${subset}/${chunk}/spectrogram`} alt="thumbnail"
             class=" object-scale-down w-full"/>
    </div>
    <div class="border-t-[1px] border-solid border-indigo-500 w-full flex flex-col items-center">
        <p class="text-center text-indigo-600 font-semibold">Time Delay Embedding</p>
        <img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail"
             class="object-scale-down w-2/3"/>
    </div>
</div>