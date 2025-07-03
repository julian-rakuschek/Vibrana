<script lang="ts">
	import FancyButton from '@components/atoms/FancyButton.svelte';
	import { Forward, Pause, Play, PlayPause } from 'svelte-hero-icons';
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import { onMount } from 'svelte';
	import RangeSlider from 'svelte-range-slider-pips';

	export let dataset: string;
	export let subset: string;
	let threads = 0;
	
	
	async function setThreads(new_threads: number) {
		await ApiRoutes.setTargetThreads.fetch({ params: {dataset, subset}, data: {threads: new_threads}})
	}

	async function getThreads(): Promise<number> {
		return await ApiRoutes.getTargetThreads.fetch({ params: {dataset, subset}})
	}

	async function oneStep() {
		await ApiRoutes.computeSingleStep.fetch({ params: {dataset, subset}})
	}

	onMount(async () => {
		threads = await getThreads();
	})
</script>

<div class="flex flex-row gap-2">
	<button class="h-10 w-10" on:click={async () => {threads = 0; await setThreads(0)}}>
		<FancyButton icon="{Pause}" button_color="primary" />
	</button>
	<button class="h-10 w-10" on:click={async () => {threads = 0; await setThreads(0); await oneStep()}}>
		<FancyButton icon="{PlayPause}" button_color="primary" />
	</button>
	<button class="h-10 w-10" on:click={async () => {threads = 1; await setThreads(1);}}>
		<FancyButton icon="{Play}" button_color="primary" />
	</button>
	<button class="h-10 w-10" on:click={async () => {threads = 10; await setThreads(10);}}>
		<FancyButton icon="{Forward}" button_color="primary" />
	</button>
	<div class="w-52">
		<RangeSlider min={0} max={10} bind:value={threads} on:stop={(e) => setThreads(e.detail.value)} pips first last float suffix=" threads" />
	</div>
</div>
