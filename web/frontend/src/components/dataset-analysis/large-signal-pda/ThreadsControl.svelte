<script lang="ts">
	import FancyButton from '@components/atoms/FancyButton.svelte';
	import { Forward, Pause, Play, PlayPause, Trash } from 'svelte-hero-icons';
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import { onMount } from 'svelte';
	import RangeSlider from 'svelte-range-slider-pips';
	import type { ClusterDelta, Fingerprint } from '@lib/types';

	export let dataset: string;
	export let subset: string;
	let running = false;
	export let handleReset: () => void;
	export let handleSingleItem: (new_fingerprint: Fingerprint, label_delta: ClusterDelta) => void;

	async function activateComputing() {
		await ApiRoutes.activateComputing.fetch({ params: { dataset, subset } });
		running = true;
	}

	async function pauseComputing() {
		await ApiRoutes.pauseComputing.fetch({ params: { dataset, subset } });
		running = false;
	}

	async function getComputingStatus(): Promise<boolean> {
		return await ApiRoutes.computingStatus.fetch({ params: { dataset, subset } });
	}

	async function oneStep() {
		const data = await ApiRoutes.computeSingleStep.fetch({ params: { dataset, subset } });
		if (handleSingleItem) handleSingleItem(data.new_fingerprint, data.label_delta);
	}

	async function clearVectors() {
		await ApiRoutes.clearFingerprints.fetch({ params: { dataset, subset } });
		if (handleReset) handleReset();
	}

	onMount(async () => {
		running = await getComputingStatus();
	});
</script>

<div class="flex flex-row gap-2 items-center justify-center">
	<button class="h-10 w-10" on:click={async () => {await pauseComputing(); await clearVectors()}}>
		<FancyButton icon="{Trash}" button_color="danger" />
	</button>
	<button class="h-10" on:click={async () => {await pauseComputing(); await oneStep()}}>
		<FancyButton button_color="primary" text="Single Step" />
	</button>
	<button class="h-10 w-10" on:click={async () => {await pauseComputing();}}>
		<FancyButton icon="{Pause}" button_color="primary" />
	</button>

	<button class="h-10 w-10" on:click={async () => {await activateComputing();}}>
		<FancyButton icon="{Play}" button_color="primary" />
	</button>
	{#if running}
		<div class="bg-green-500 text-white px-4 pb-1 mt-2 pt-0.5 rounded-full">Computation is running.</div>
	{:else}
		<div class="bg-gray-600 text-white px-4 pb-1 mt-2 pt-0.5 rounded-full">Computation is paused.</div>
	{/if}
</div>
