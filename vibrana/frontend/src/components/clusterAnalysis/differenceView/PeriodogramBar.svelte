<script lang="ts">
    import {onMount} from "svelte";

    interface Props {
        periodogram: number[];
        color: string;
        width?: number;
        height?: number;
        global_max?: number;
    }

    let { periodogram, color, width = 1000, height = 100, global_max }: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;

    function render(periodogram: number[]) {
        if (!canvas || !context) return;
        context.clearRect(0, 0, width, height);
        context.globalAlpha = 0.2;
        context.fillStyle = color;
        context.fillRect(0, 0, width, height);
        context.globalAlpha = 1;
        const bar_width = width / periodogram.length;
        const max_value = global_max ?? Math.max(...periodogram);
        for (let i = 0; i < periodogram.length; i++) {
            const bar_height = (periodogram[i] / max_value) * height;
            context.fillRect(i * bar_width, height, bar_width, -bar_height);
        }
    }

    onMount(async () => {
        if (!canvas) return;
        context = canvas.getContext('2d');
        render(periodogram);
    });

    $effect(() => {
        render(periodogram);
    });
</script>

<canvas {height} {width} bind:this={canvas}></canvas>