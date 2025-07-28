<script lang="ts">
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import PDAThreadsControl from '@components/pda/PDAThreadsControl.svelte';
	import PDAVis from '@components/pda/PDAVis.svelte';
	import { io } from 'socket.io-client';
	import type { ClusterHistogram, Fingerprint } from '@lib/types';
	import { onMount } from 'svelte';

	export let dataset = 'hydro';
	export let subset = 'x';
	const socket = io('http://localhost:5000');

	let fingerprints: Fingerprint[] = [];
	let colors: string[] = [];
	let pdaVis: PDAVis;
	let cluster_histogram: ClusterHistogram = [];

	socket.on('connect', () => {
		const room = `vibrana:${dataset}:${subset}`;
		socket.emit('join', { room });
	});

	socket.on('message', (data) => {
		console.log(data)
		addNewItem(data["new_fingerprint"], data["label_delta"]);
	});

	function addNewItem(new_fingerprint: Fingerprint, label_delta: {index: number; new_label: number}[]) {
		console.log(label_delta)
		new_fingerprint["index"] = fingerprints.length;
		fingerprints = [...fingerprints, new_fingerprint];
		colors = [...colors, "gray"];
		pdaVis.drawVectors(fingerprints, colors);
	}

	async function fetchAndDrawAll() {
		let vectors_query = await ApiRoutes.getFingerprints.fetch({ params: { dataset, subset } })
		for (let i = 0; i < vectors_query.length; i++) {
			vectors_query[i]["index"] = i;
		}
		fingerprints = [...vectors_query]
		pdaVis.drawVectors(fingerprints, colors);
	}

	onMount(async () => {
		await fetchAndDrawAll();
	})

</script>

<div class="grid grid-cols-3 px-10">
	<PDAThreadsControl dataset={dataset} subset={subset} handleReset={() => fetchAndDrawAll()} handleSingleItem={(data) => addNewItem(data)} />
	<p class="self-center text-center text-xl font-bold">Long Signal Analysis</p>
	<p class="self-center text-right">{fingerprints.length} Fingerprints</p>
</div>
<PDAVis vectors={fingerprints} colors={colors} bind:this={pdaVis} dataset={dataset} subset={subset} cluster_histogram={cluster_histogram} />