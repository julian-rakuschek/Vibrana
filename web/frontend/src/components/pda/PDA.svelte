<script lang="ts">
	import { useQueryFetch } from '@lib/api/ApiQueries';
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import PDAThreadsControl from '@components/pda/PDAThreadsControl.svelte';
	import PDAVis from "@components/pda/PDAVis.svelte";
	import { io } from 'socket.io-client';
	import type {HyperplaneVector} from "@lib/types";
	import {onMount} from "svelte";

	export let dataset = 'hydro';
	export let subset = 'x';
	const socket = io('http://localhost:5000');

	let vectors: HyperplaneVector[] = [];
	let pdaVis: PDAVis;

	socket.on('connect', () => {
		const room = 'vibrana:hydro:x';
		socket.emit('join', { room });
	});

	socket.on('message', (data) => {
		console.log(data);
		vectors = [...vectors, data];
		if (pdaVis) pdaVis.addRectangle(data);
	});

	async function fetchAndDrawAll() {
		console.log("called")
		let vectors_query = await ApiRoutes.getVectors.fetch({ params: { dataset, subset } })
		vectors = [...vectors_query]
		if (pdaVis) {
			pdaVis.drawVectors(vectors);
		}
	}

	onMount(async () => {
		await fetchAndDrawAll();
	})

</script>

<div class="grid grid-cols-3 px-10">
	<PDAThreadsControl dataset={dataset} subset={subset} handleReset={() => fetchAndDrawAll()} />
	<p class="self-center text-center text-xl font-bold">Long Signal Analysis</p>
	<p class="self-center text-right">{vectors.length} Fingerprints</p>
</div>
<PDAVis vectors={vectors} bind:this={pdaVis} />
