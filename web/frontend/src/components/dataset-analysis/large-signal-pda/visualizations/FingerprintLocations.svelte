<script lang="ts">
    import type {Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import FingerprintRendering from "@components/atoms/FingerprintRendering.svelte";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[] = [];
    export let colors: string[] = [];
    export let dataProvider: DataProvider;
    let loading = dataProvider.loading;

    let container: HTMLDivElement;
    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 100;
    let index_allocation: number[] = new Array(width).fill(-1);
    let currently_hovering = -1;
    let fingerprint_position = -1;

    export function addVector(vec: Fingerprint, color?: string) {
        if (!context) return;
        const start = Math.floor((vec.start_index / vec.max_index) * width);
        const rectangle_width = Math.floor((vec.slice_length / vec.max_index) * width);
        context.fillStyle = color ?? 'red';
        context.fillRect(start, 0, rectangle_width, height);
        for (let j = 0; j < rectangle_width; j++) {
            index_allocation[start + j] = vec.index;
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

    function get_nearest_fingerprint(index: number) {
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
    }

    onMount(async () => {
        context = canvas.getContext('2d');
        canvas.onmousemove = (e) => {
            const x = e.clientX - canvas.getBoundingClientRect().left;
            get_nearest_fingerprint(Math.floor(x));
        };
        drawVectors(fingerprints, colors);
    });

    $: {
        if (fingerprints.length === 0) index_allocation = new Array(width).fill(-1);
        drawVectors(fingerprints, colors);
    }
</script>

<div bind:this={container} class="w-full" on:mouseleave={() => currently_hovering = -1}>
    <canvas {height} {width} bind:this={canvas}></canvas>
</div>
<div class="relative w-full" style={`width: ${width}px;`}>
    {#if currently_hovering !== -1}
        <div class="absolute bg-indigo-800 w-[50px] h-[50px] -translate-x-1/2 rotate-45"
             style={`left: ${fingerprint_position}px`}></div>
        <div class="absolute mt-3 p-3 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
             style={`left: ${fingerprint_position}px`}>
            {#if $loading}
                <CenteredLoadingSpinner/>
            {:else}
                <FingerprintRendering {dataProvider} fingerprint={fingerprints[currently_hovering]}/>
            {/if}
        </div>
    {/if}
</div>


