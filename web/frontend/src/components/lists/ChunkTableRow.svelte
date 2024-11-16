<script lang="ts">
	import {ArrowTopRightOnSquare, Eye, Icon} from 'svelte-hero-icons';
	import type {AnomalyMetric, SelectedChunk} from '@lib/types';
	import DistanceIndicator from '@components/similarities/DistanceIndicator.svelte';
	import {itemSeen, sessionResetChunk, sessionToggleNormal} from '@lib/helper/sessionStorageHelper';
	import {ApiRoutes} from '@lib/api/ApiRoutes';
	import {getContext} from 'svelte';
	import {useQueryClient} from '@tanstack/svelte-query';
	import Toggle from '@components/atoms/Toggle.svelte';
	import ImageWithLightbox from '@components/atoms/ImageWithLightbox.svelte';
	import {simpleTable, selectedChunk} from '@lib/stores';

	export let isNormal: boolean;
	export let dataset: string;
	export let subset: string;
	export let chunk: string;
	export let anomaly: AnomalyMetric | undefined;
	export let normalTube: [number, number];
	export let labelCount: number;

	const { ro } = getContext('ro') as { ro: boolean };
	const client = useQueryClient();

	const toggleNormal = async () => {
		if (ro) sessionToggleNormal(dataset, subset, chunk);
		else await ApiRoutes.toggleNormal.fetch({ params: { dataset, subset, chunk } });
		await client.invalidateQueries();
	};

	const resetChunk = async () => {
		if (ro) sessionResetChunk(dataset, subset, chunk);
		else await ApiRoutes.resetChunk.fetch({ params: { dataset, subset, chunk } });
		await client.invalidateQueries();
	};

	const isSelected = (global?: SelectedChunk) => {
        if (!global) return false;
        return global.chunk === chunk && global.subset === subset && global.dataset === dataset
    }

</script>


<tr class={`${isSelected($selectedChunk) ? "bg-indigo-700 text-white" : "even:bg-gray-50 text-gray-500"} transition`}
	on:click={() => selectedChunk.set({dataset, subset, chunk})}
>
	<td class="whitespace-nowrap text-sm text-left font-medium text-gray-900 sm:pl-3">
		<a
			class={`flex flex-row gap-1 items-center text-center font-semibold
			${isSelected($selectedChunk) ? "text-white hover:text-white hover:border-white" : "text-indigo-600 hover:text-indigo-800 hover:border-indigo-800"}
			`}
			href={`/datasets/${dataset}/${subset}/${chunk}`}
		>
			<span class={isSelected($selectedChunk) ? "border-dotted border-b-2 border-b-white" : "border-dotted border-b-2 border-b-indigo-600"}>{chunk}</span>
			<Icon src="{ArrowTopRightOnSquare}" solid class={isSelected($selectedChunk) ? "w-4 h-4 text-white" : "w-4 h-4 text-indigo-600"} />
		</a>
	</td>
	{#if !$simpleTable}
		<td class="whitespace-nowrap text-sm text-center">{anomaly?.count ?? 0}</td>
		<td class="whitespace-nowrap text-sm text-center">{labelCount}</td>
	{/if}
	<td class="whitespace-nowrap text-sm text-left">
		<ImageWithLightbox src={`/api/db/${dataset}/${subset}/${chunk}/thumbnail`} alt="thumbnail" classNames="object-contain h-[100px]" />
		{#if anomaly !== undefined && !$simpleTable}
			<div class="h-[10px] w-[315px]">
				<DistanceIndicator distances={anomaly.distances_reduced} normalTube={normalTube} />
			</div>
		{/if}
	</td>
	<td class="whitespace-nowrap text-sm text-left">
		<ImageWithLightbox src={`/api/db/${dataset}/${subset}/${chunk}/spectrogram`} alt="thumbnail" classNames="object-contain h-[100px]" />
	</td>
	<td class="whitespace-nowrap text-sm text-left">
		<ImageWithLightbox src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail" classNames="object-contain h-[100px]" />
	</td>
	{#if !$simpleTable}
		<td class="relative whitespace-nowrap text-center text-sm font-medium sm:pr-3">
			{#if itemSeen(dataset, subset, chunk)}
				<Icon src="{Eye}" solid class="w-6 h-6 text-indigo-400" />
			{/if}
		</td>
		<td class="relative whitespace-nowrap text-center text-sm font-medium sm:pr-3">
			<Toggle bind:enabled={isNormal} onToggle={() => toggleNormal()} />
		</td>
		<td class="relative whitespace-nowrap text-center text-sm font-medium sm:pr-3">
			<button on:click={() => resetChunk()} class="rounded-lg px-2 py-1 bg-indigo-50 text-indigo-600 text-sm transition hover:bg-red-500 hover:text-white">Reset labels</button>
		</td>
	{/if}
</tr>