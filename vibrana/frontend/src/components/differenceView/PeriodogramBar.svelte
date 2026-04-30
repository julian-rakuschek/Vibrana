<script lang="ts">
    import {onMount} from "svelte";

    interface Props {
        periodogram: number[];
        color_fg: string;
        color_bg: string;
        width?: number;
        height?: number;
        global_max?: number;
    }

    let { periodogram, color_fg, color_bg, width = 1000, height = 100, global_max }: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;

    function render(periodogram: number[]) {
        if (!canvas || !context) return;
        context.clearRect(0, 0, width, height);
        context.fillStyle = color_bg;
        context.fillRect(0, 0, width, height);
        const bar_width = width / periodogram.length;
        const max_value = global_max ?? Math.max(...periodogram);
        context.fillStyle = color_fg;
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