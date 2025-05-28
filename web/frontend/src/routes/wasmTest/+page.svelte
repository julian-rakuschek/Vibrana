<script lang="ts">
	import createPCA from './pca.js';
	import { getContext, onMount } from 'svelte';
	import { useQueryFetch } from '@lib/api/ApiQueries.js';
	import { ApiRoutes } from '@lib/api/ApiRoutes.js';
	import type { ProjectedPoint } from '@lib/types';
	import ScatterPlot from '@components/detail-view/ScatterPlot.svelte';

	let dataset = 'hydro';
	let subset = 'hydro-1-x';
	let chunk = 'hydro-1-x-0000';
	const timeSeriesQuery = useQueryFetch(ApiRoutes.getChunkValues, { params: { dataset, subset, chunk } });
	let tsData: number[] = [];
	let wasmPCA = undefined;
	let projectedIndexed: ProjectedPoint[] = [];

	const indexProjectedPoints = (data: number[][]) => {
		const offset = tsData.length - data.length;
		projectedIndexed = data.map((d, i): ProjectedPoint => ({
			projectedIndex: i,
			timeSeriesIndex: i + Math.floor(offset / 2),
			coords: d
		}));
		return projectedIndexed;
	};

	const computePCA = (data: number[]): number[][] => {
		if (!wasmPCA) return [];
		const vec = new wasmPCA.arrayToVec(data);
		// vec.reserve(data.length);
		console.log('vec ready');
		const tde = wasmPCA.slidingWindowView(vec, 1000, 0, data.length - 1);
		console.log(tde)
		const pc = wasmPCA.getPrincipalComponents(tde);
		console.log(pc)
		// const projected = wasmPCA.project(pc, tde);
		// const projected_js = wasmPCA.matrixToArray(projected);
		// console.log(projected_js);
		// indexProjectedPoints(projected_js);
		// return projected_js;
	};

	onMount(async () => {
		wasmPCA = await createPCA();
	});

	timeSeriesQuery.subscribe((data) => {
		if (data.data) tsData = data.data;
	});

	const handleHover = () => {
		console.log('hover start');
		const res = computePCA(tsData);
		console.log(res);
	};


</script>

<p>Hi WASM</p>
<button on:click={() => handleHover()}>Click me</button>
{#if projectedIndexed.length > 0}
<ScatterPlot dataset={dataset} subset={subset} chunk={chunk} timeSeries={tsData} projected={projectedIndexed} colors={[]}  />
	{/if}