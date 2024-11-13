<script lang="ts">
    import {Icon, CheckCircle, ArrowTopRightOnSquare, Eye} from "svelte-hero-icons";
    import AnomalyRatio from "@components/AnomalyRatio.svelte";
    import type {AnomalyMetric} from "@lib/types";
    import DistanceIndicator from "@components/DistanceIndicator.svelte";
    import {itemSeen, sessionResetChunk, sessionToggleNormal} from "@lib/helper/sessionStorageHelper";
    import AnomalyCount from "@components/AnomalyCount.svelte";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {getContext} from "svelte";
    import {useQueryClient} from "@tanstack/svelte-query";
    import Toggle from "@components/atoms/Toggle.svelte";
    import ImageWithLightbox from '@components/atoms/ImageWithLightbox.svelte';

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
        if (ro) sessionResetChunk(dataset, subset, chunk)
        else await ApiRoutes.resetChunk.fetch({params: {dataset, subset, chunk}})
        await client.invalidateQueries();
    }

</script>


<tr class="even:bg-gray-50">
    <td class="whitespace-nowrap text-sm text-left font-medium text-gray-900 sm:pl-3">
        <a
                class="flex flex-row gap-1 items-center text-center font-semibold text-indigo-600 hover:text-indigo-800 hover:border-indigo-800"
                href={`/datasets/${dataset}/${subset}/${chunk}`}
        >
            <span class=" border-dotted border-b-2 border-b-indigo-600">{chunk}</span>
            <Icon src="{ArrowTopRightOnSquare}" solid class="w-4 h-4 text-indigo-600"/>
        </a>
    </td>
    <td class="whitespace-nowrap text-sm text-center text-gray-500">{anomaly?.count ?? 0}</td>
    <td class="whitespace-nowrap text-sm text-center text-gray-500">{labelCount}</td>
    <td class="whitespace-nowrap text-sm text-left text-gray-500">
        <ImageWithLightbox src={`/api/db/${dataset}/${subset}/${chunk}/thumbnail`} alt="thumbnail" classNames="object-contain h-[100px]"/>
        {#if anomaly !== undefined}
            <div class="w-full h-[10px]">
                <DistanceIndicator distances={anomaly.distances_reduced} normalTube={normalTube} width={320} height={10}/>
            </div>
        {/if}
    </td>
    <td class="whitespace-nowrap text-sm text-left text-gray-500">
        <ImageWithLightbox src={`/api/db/${dataset}/${subset}/${chunk}/spectrogram`} alt="thumbnail" classNames="object-contain h-[100px]"/>
    </td>
    <td class="whitespace-nowrap text-sm text-left text-gray-500">
        <ImageWithLightbox src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail" classNames="object-contain h-[100px]"/>
    </td>
    <td class="relative whitespace-nowrap text-center text-sm font-medium sm:pr-3">
        {#if itemSeen(dataset, subset, chunk)}
            <Icon src="{Eye}" solid class="w-6 h-6 text-indigo-400"/>
        {/if}
    </td>
    <td class="relative whitespace-nowrap text-center text-sm font-medium sm:pr-3">
        <Toggle bind:enabled={isNormal} onToggle={() => toggleNormal()}/>
    </td>
    <td class="relative whitespace-nowrap text-center text-sm font-medium sm:pr-3">
        <button on:click={() => resetChunk()} class="rounded-lg px-2 py-1 bg-indigo-50 text-indigo-600 text-sm transition hover:bg-red-500 hover:text-white">Reset labels</button>
    </td>
</tr>