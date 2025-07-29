<script lang="ts">
    import type {Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {DataProvider} from '@lib/dataProvider/dataProvider';
    import {interpolateTurbo} from 'd3';

    export let dataProvider: DataProvider;
	export let fingerprint: Fingerprint | null;
    export let size = 200;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;

	export function visualizeFingerprint(fp: Fingerprint) {
		const projected = dataProvider.get_fingerprint_data_javascript(fp);

		const min_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[0];
		const max_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[projected.length - 1];
		const min_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[0];
		const max_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[projected.length - 1];

		if (!context) return;
		context.fillStyle = '#FFFFFF';
		context.fillRect(0, 0, size, size);

		for (let i = 0; i < projected.length; i++) {
			const x = (projected[i][0] - min_x_value) / (max_x_value - min_x_value);
			const y = (projected[i][1] - min_y_value) / (max_y_value - min_y_value);
			const radius = Math.sqrt(Math.pow(x - 0.5, 2) + Math.pow(y - 0.5, 2)) * 2;
            context.fillStyle = interpolateTurbo(radius);
			context.fillRect(x * size, y * size, 1, 1);
		}
	}

	onMount(async () => {
		context = canvas.getContext('2d');
		if (fingerprint) visualizeFingerprint(fingerprint);
	});

	$: if (fingerprint) visualizeFingerprint(fingerprint);

</script>

<canvas height={size} width={size} bind:this={canvas}></canvas>
