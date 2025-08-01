<script lang="ts">
    import {onMount} from 'svelte';

    export let dataset: string;
    export let subset: string;
    export let index_allocation: number[] = [];
    export let colors: string[] = [];
    export let width = 1000;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    const height = 100;

    export function render(index_allocation: number[], colors?: string[]) {
        if (!context) return;
        context.clearRect(0, 0, width, height);
        for (let i = 0; i < width; i++) {
            const allocated = index_allocation[i]
            if (allocated !== -1) {
                context.fillStyle = colors && colors.length > allocated ? colors[allocated] : "red";
								context.fillRect(i, 0, 1, height);
            }

        }
    }

    onMount(async () => {
        context = canvas.getContext('2d');
        render(index_allocation, colors);
    });

    $: {
        if (index_allocation.length === 0) index_allocation = new Array(width).fill(-1);
        render(index_allocation, colors);
    }
</script>

<canvas {height} {width} bind:this={canvas}></canvas>


