<script lang="ts">
    import {onMount} from 'svelte';
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";

    export let dataset: string;
    export let subset: string;
    export let label_allocation: number[] = [];
    export let colorMapping: ClusterColorMapping;
    export let width = 1000;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    const height = 100;

    export function render(label_allocation: number[]) {
        if (!context || label_allocation.length === 0) return;
        context.clearRect(0, 0, width, height);
        for (let i = 0; i < width; i++) {
            const allocated = label_allocation[i]
            if (allocated !== null) {
                context.fillStyle = colorMapping[allocated]
                context.fillRect(i, 0, 1, height);
            }

        }
    }

    onMount(async () => {
        context = canvas.getContext('2d');
        render(label_allocation);
    });

    $: render(label_allocation);
</script>

<canvas {height} {width} bind:this={canvas}></canvas>


