<script lang="ts">
	import type { ClusterColorMapping } from '@lib/types';
	import { onMount } from 'svelte';
	import { fillGaps } from '@lib/algorithms/gapFill';

	export let colorMapping: ClusterColorMapping;
	export let label_allocation: number[] = [];
	export let width = 1000;

	let canvas: HTMLCanvasElement;
	let context: CanvasRenderingContext2D | null;
	const height = 100;

	function render(labelAllocation: number[]) {
		if (!context) return;
		context.clearRect(0, 0, width, height);
		context.fillStyle = '#FFFFFF';
		context.fillRect(0, 0, width, height);
		if (labelAllocation.length !== width) return;
		const filledGaps = fillGaps(labelAllocation, null);
		if (filledGaps[0] === null) return;
		for (let i = 0; i < width; i++) {
			const label = filledGaps[i];
			context.globalAlpha = 0.2;
			context.fillStyle = label === null ? 'lightgray' : colorMapping[label];
			context.fillRect(i, 0, 1, height);
		}
	}

	onMount(async () => {
		context = canvas.getContext('2d');
		render(label_allocation);
	});

	$: render(label_allocation);
</script>

<div class="w-full">
	<canvas {height} {width} bind:this={canvas}></canvas>
</div>