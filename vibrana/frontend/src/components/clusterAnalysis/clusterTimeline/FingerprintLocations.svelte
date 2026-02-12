<script lang="ts">
    import {onMount} from 'svelte';
    import type {ClusterColorMapping} from "@lib/types";

    interface Props {
        label_allocation?: number[];
        colorMapping: ClusterColorMapping;
        width?: number;
    }

    let { label_allocation = [], colorMapping, width = 1000 }: Props = $props();

    let canvas: HTMLCanvasElement = $state();
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

    $effect(() => {
        render(label_allocation);
    });
</script>

<canvas {height} {width} bind:this={canvas}></canvas>


