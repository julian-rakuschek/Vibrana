<script lang="ts">
	import type { ClusterHistogram, Fingerprint } from '@lib/types';
	import { onMount } from 'svelte';
	import { DataProvider } from '@lib/dataProvider/dataProvider';
	import { page } from '$app/stores';
	import FingerprintVis from '@components/pda/FingerprintVis.svelte';
	import PDAAging from '@components/pda/PDAAging.svelte';
	import PDASteering from '@components/pda/PDASteering.svelte';
	import { fillGaps } from '@lib/algorithms/gapFill';
	import PDAOverview from '@components/pda/PDAOverview.svelte';

	export let fingerprints: Fingerprint[] = [];
	export let cluster_histogram: ClusterHistogram = [];
	export let colors: string[] = [];
	export let dataset: string;
	export let subset: string;

	console.log(fingerprints);

	let canvas: HTMLCanvasElement;
	let context: CanvasRenderingContext2D | null;
	const width = 1000;
	const height = 100;
	const index_allocation: number[] = new Array(width).fill(-1);
	const label_allocation: number[] = new Array(width).fill(null);
	let currently_hovering = -1;
	let fingerprint_position = -1;
	let dataProvider: DataProvider;


	export function addVector(vec: Fingerprint, color?: string) {
		if (!context) return;
		const start = Math.floor((vec.start_index / vec.max_index) * width);
		const rectangle_width = Math.floor((vec.slice_length / vec.max_index) * width);
		context.fillStyle = color ?? 'red';
		context.fillRect(start, 0, rectangle_width, height);
		for (let j = 0; j < rectangle_width; j++) {
			index_allocation[start + j] = vec.index;
			label_allocation[start + j] = vec.label;
		}
	}

	export function drawVectors(vectors_to_draw: Fingerprint[], colors?: string[]) {
		if (!context) return;
		context.fillStyle = '#eeeeee';
		context.fillRect(0, 0, width, height);
		for (let i = 0; i < vectors_to_draw.length; i++) {
			addVector(vectors_to_draw[i], colors && i < colors.length ? colors[i] : 'red');
		}
	}

	onMount(async () => {
		context = canvas.getContext('2d');
		dataProvider = new DataProvider(
			dataset, subset,
			$page.data.config[dataset].subsets[subset].sliding_window_size,
			$page.data.config[dataset].in_memory
		);
		await dataProvider.load();
		canvas.onmousemove = (e) => {
			const r = canvas.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
			const index = Math.floor(x);
			if (index >= index_allocation.length || index < 0) return;
			let step = 0;
			currently_hovering = -1;
			fingerprint_position = -1;
			while (step < index_allocation.length) {
				const left = index - step >= 0 ? index - step : 0;
				const right = index + step < index_allocation.length ? index + step : index_allocation.length - 1;
				if (index_allocation[left] !== -1) {
					currently_hovering = index_allocation[left];
					fingerprint_position = left;
					break;
				}
				if (index_allocation[right] !== -1) {
					currently_hovering = index_allocation[right];
					fingerprint_position = right;
					break;
				}
				step++;
			}
		};
		drawVectors(fingerprints, colors);
	});
</script>

<div class="grid grid-cols-2">
	<div class="flex flex-col p-4">
		<div>
			<PDAOverview fingerprints={fingerprints} label_allocation={label_allocation} />
		</div>
		<div on:mouseleave={() => currently_hovering = -1}>
			<canvas height={height} width={width} bind:this={canvas}></canvas>
		</div>
		<div class="relative w-full" style={`width: ${width}px;`}>
			{#if currently_hovering !== -1}
				<div class="absolute bg-indigo-800 w-[50px] h-[50px] -translate-x-1/2 rotate-45"
						 style={`left: ${fingerprint_position}px`}></div>
				<div class="absolute mt-3 p-3 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
						 style={`left: ${fingerprint_position}px`}>
					<FingerprintVis dataProvider={dataProvider} hyperplane={fingerprints[currently_hovering]} />
				</div>
			{/if}
		</div>
		<div>
			<PDASteering aging={index_allocation} dataset={dataset} subset={subset} />
		</div>
	</div>
	<div class="px-6">
		<p class="text-lg text-center mb-2">Cluster Distribution</p>
		<div class="grid grid-cols-6 place-items-start gap-2">
			{#each cluster_histogram as cluster}
				<p class="text-right place-self-end" style={`color: ${cluster.color}`}>{cluster.cluster_id}</p>
				<div class="h-[20px] col-span-4" style={`background-color: ${cluster.color}; width: ${cluster.relative_size * 100}%`}></div>
				<p style={`color: ${cluster.color}`}>{cluster.size} members</p>
			{/each}
		</div>
	</div>

</div>


