<script lang="ts">
	import type {ClusterColorMapping, Fingerprint} from '@lib/types';
	import { onMount } from 'svelte';
	import {AVLTree} from "avl";
	import {findNearestFingerprint} from "@lib/helper/util";
	import {fingerprintMode} from "@lib/stores";

	interface Props {
		colorMapping: ClusterColorMapping;
		visibleIndices?: number[];
		width?: number;
		fp_tree: AVLTree<number, Fingerprint>;
	}

	let { colorMapping, visibleIndices = [], width = 1000, fp_tree }: Props = $props();

	let canvas: HTMLCanvasElement = $state();
	let context: CanvasRenderingContext2D | null;
	const height = 100;

	function render(visibleIndices: number[], feature: "tde" | "psd") {
		if (!context) return;
		context.clearRect(0, 0, width, height);
		context.fillStyle = '#FFFFFF';
		context.fillRect(0, 0, width, height);
		// console.log(visibleIndices)
		for (let i = 0; i < visibleIndices.length; i++) {
			const label = findNearestFingerprint(visibleIndices[i], fp_tree)?.label[feature] ?? null;
			// console.log(label)
			context.globalAlpha = 0.2;
			context.fillStyle = label === null ? 'lightgray' : colorMapping[label];
			context.fillRect(i, 0, 1, height);
		}
	}

	onMount(async () => {
		context = canvas.getContext('2d');
		render(visibleIndices, $fingerprintMode);
	});

	$effect(() => {
		render(visibleIndices, $fingerprintMode);
	});

	fingerprintMode.subscribe(fm => render(visibleIndices, fm));
</script>

<div class="w-full">
	<canvas {height} {width} bind:this={canvas}></canvas>
</div>