<script lang="ts">
    import {onMount} from "svelte";
    import {interpolateRdBu} from "d3";

    interface Props {
        periodogram1: number[];
        periodogram2: number[];
        width?: number;
        height?: number;
        global_max?: number;
    }

    let { periodogram1, periodogram2, width = 1000, height = 100, global_max }: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;

    function render(periodogram1: number[], periodogram2: number[]) {
        if (!canvas || !context) return;
        context.clearRect(0, 0, width, height);
        const len = Math.min(periodogram1.length, periodogram2.length);
        const bar_width = width / len;
        const max_delta = global_max ?? Math.max(...periodogram1, ...periodogram2);

        for (let i = 0; i < len; i++) {
            const diff = periodogram1[i] - periodogram2[i];
            const normalized = (diff + max_delta) / (2 * max_delta)
            context.fillStyle = interpolateRdBu(normalized);
            context.fillRect(i * bar_width, 0, bar_width, height);
        }

    }

    onMount(async () => {
        if (!canvas) return;
        context = canvas.getContext('2d');
        render(periodogram1, periodogram2);
    });

    $effect(() => {
        render(periodogram1, periodogram2);
    });
</script>

<canvas {height} {width} bind:this={canvas}></canvas>