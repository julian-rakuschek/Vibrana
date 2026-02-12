<script lang="ts">
    import type {Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {DataProvider} from '@lib/dataProvider/dataProvider';
    import {interpolateTurbo} from 'd3';

    interface Props {
        dataProvider: DataProvider;
        fingerprint: Fingerprint | null;
        size?: number;
        transparent?: boolean;
        color?: string | null;
        update_on_fp_change?: boolean;
    }

    let {
        dataProvider,
        fingerprint,
        size = 200,
        transparent = false,
        color = null,
        update_on_fp_change = true
    }: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;

    function visualizeFingerprint(fp: Fingerprint) {
        const projected = dataProvider.get_fingerprint_data_javascript(fp);

        const min_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[0];
        const max_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[projected.length - 1];
        const min_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[0];
        const max_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[projected.length - 1];

        if (!context || !canvas) return;
        if (!transparent) {
            context.fillStyle = '#FFFFFF';
            context.fillRect(0, 0, size, size);
        }


        for (let i = 0; i < projected.length; i++) {
            const x = (projected[i][0] - min_x_value) / (max_x_value - min_x_value);
            const y = (projected[i][1] - min_y_value) / (max_y_value - min_y_value);
            const radius = Math.sqrt(Math.pow(x - 0.5, 2) + Math.pow(y - 0.5, 2)) * 2;
            context.fillStyle = color ?? interpolateTurbo(radius);
            context.fillRect(x * size, y * size, 1, 1);
        }
    }

    onMount(async () => {
        if (canvas) {
            context = canvas.getContext('2d');
        }
        if (fingerprint) visualizeFingerprint(fingerprint);
    });

    $effect(() => {
        if (!canvas) return;
        context ??= canvas.getContext('2d');
        if (fingerprint && update_on_fp_change) visualizeFingerprint(fingerprint);
    });


</script>

<canvas height={size} width={size} bind:this={canvas}></canvas>
