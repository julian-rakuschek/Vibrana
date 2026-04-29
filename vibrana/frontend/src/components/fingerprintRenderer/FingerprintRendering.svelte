<script lang="ts">
    import type {Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {DataProvider} from '@lib/dataProvider/dataProvider';
    import {interpolateTurbo} from 'd3';
    import CenteredLoadingSpinner from '@components/atoms/CenteredLoadingSpinner.svelte';

    interface Props {
        dataProvider: DataProvider;
        fingerprint: Fingerprint | null;
        size?: number;
        transparent?: boolean;
        color?: string | null;
        cache_projection?: boolean;
    }

    let {
        dataProvider,
        fingerprint,
        size = 200,
        transparent = false,
        color = null,
        cache_projection = false
    }: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;
    let cached_projection: number[][] | null = null;
    let render_generation = 0;
    let loading_projection = $state(false);

    async function visualizeFingerprint(fp: Fingerprint) {
        const generation = ++render_generation;
        if (cached_projection === null || !cache_projection) {
            if (dataProvider.isInMemory()) {
                cached_projection = dataProvider.compute_in_memory_projection(fp);
            } else {
                loading_projection = true;
                try {
                    cached_projection = await dataProvider.fetch_projection(fp);
                } finally {
                    if (generation === render_generation) {
                        loading_projection = false;
                    }
                }
            }
        }
        if (generation !== render_generation) return;
        if (!cached_projection) return;
        const projected = cached_projection;
        if (!context || !canvas) return;

        context.clearRect(0, 0, size, size);
        if (!transparent) {
            context.fillStyle = '#FFFFFF';
            context.fillRect(0, 0, size, size);
        }
        if (projected.length === 0) return;

        const min_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[0];
        const max_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[projected.length - 1];
        const min_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[0];
        const max_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[projected.length - 1];
        const x_range = max_x_value - min_x_value || 1;
        const y_range = max_y_value - min_y_value || 1;


        for (let i = 0; i < projected.length; i++) {
            const x = (projected[i][0] - min_x_value) / x_range;
            const y = (projected[i][1] - min_y_value) / y_range;
            const radius = Math.sqrt(Math.pow(x - 0.5, 2) + Math.pow(y - 0.5, 2)) * 2;
            context.fillStyle = color ?? interpolateTurbo(radius);
            context.fillRect(x * size, y * size, 1, 1);
        }
    }

    onMount(async () => {
        if (canvas) {
            context = canvas.getContext('2d');
        }
    });

    $effect(() => {
        if (!canvas) return;
        context ??= canvas.getContext('2d');
        if (fingerprint) void visualizeFingerprint(fingerprint);
    });


</script>

<div class="relative" style={`height: ${size}px; width: ${size}px`}>
    {#if loading_projection}
        <div class="absolute inset-0 flex items-center justify-center">
            <CenteredLoadingSpinner color={color ?? undefined}/>
        </div>
    {/if}
    <canvas class:opacity-0={loading_projection} height={size} width={size} bind:this={canvas}></canvas>
</div>
