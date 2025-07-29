<script lang="ts">
	import type { Fingerprint } from '@lib/types';

	export let fingerprints: Fingerprint[] = [];
	export let label_allocation: number[] = [];

	let canvas: HTMLCanvasElement;
	let context: CanvasRenderingContext2D | null;
	const width = 1000;
	const height = 100;


</script>

<canvas height={height} width={width} bind:this={canvas}></canvas>
