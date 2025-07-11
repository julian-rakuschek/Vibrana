<script lang="ts">
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import PDAThreadsControl from '@components/pda/PDAThreadsControl.svelte';
	import PDAVis from "@components/pda/PDAVis.svelte";
	import { io } from 'socket.io-client';
	import type {HyperplaneVector} from "@lib/types";
	import {onMount} from "svelte";
	import {DBSCAN_VibrationFingerprints} from "@lib/algorithms/incrementalDBSCAN";

	export let dataset = 'hydro';
	export let subset = 'x';
	const socket = io('http://localhost:5000');

	let vectors: HyperplaneVector[] = [];
	let colors: string[] = [];
	let pdaVis: PDAVis;
	let dbscan: DBSCAN_VibrationFingerprints;

	socket.on('connect', () => {
		const room = 'vibrana:hydro:x';
		socket.emit('join', { room });
	});

	socket.on('message', (data) => {
		addNewItem(data);
	});

	function addNewItem(data: HyperplaneVector) {
		const new_index = vectors.length;
		data["index"] = new_index;
		vectors = [...vectors, data];
		const changes = dbscan.insert(data);
		colors = [...colors, dbscan.getColor(new_index)];
		if (pdaVis) {
			if (changes === 1) {
				console.log("Single change", new_index, dbscan.getColor(new_index))
				pdaVis.addVector(data, dbscan.getColor(new_index));
			}
			else {
				console.log("redraw all");
				colors = dbscan.getAllColors();
				pdaVis.drawVectors(vectors, colors);
			}
		}
	}

	async function fetchAndDrawAll() {
		let vectors_query = await ApiRoutes.getVectors.fetch({ params: { dataset, subset } })
		for (let i = 0; i < vectors_query.length; i++) {
			vectors_query[i]["index"] = i;
		}
		vectors = [...vectors_query]
		dbscan = new DBSCAN_VibrationFingerprints(0.2, 5, vectors);
		dbscan.cluster();
		colors = dbscan.getAllColors();
		if (pdaVis) {
			pdaVis.drawVectors(vectors, colors);
		}
	}

	onMount(async () => {
		await fetchAndDrawAll();
	})

</script>

<div class="grid grid-cols-3 px-10">
	<PDAThreadsControl dataset={dataset} subset={subset} handleReset={() => fetchAndDrawAll()} handleSingleItem={(data) => addNewItem(data)} />
	<p class="self-center text-center text-xl font-bold">Long Signal Analysis</p>
	<p class="self-center text-right">{vectors.length} Fingerprints</p>
</div>
<PDAVis vectors={vectors} colors={colors} bind:this={pdaVis} dataset={dataset} subset={subset} />