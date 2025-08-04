<script lang="ts">
    import {onMount} from "svelte";
    import * as d3 from 'd3';

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 50;

    export let zoom_interval: [number, number] = [0, 1];
    export let intervals: [number, number][] = [];


    function render(zoom_interval: [number, number], intervals: [number, number][]) {
        if (!context) return;
        context.globalAlpha = 1;
        context.fillStyle = '#eeeeee';
        context.fillRect(0, 0, width, height);
        for (let i = 0; i < width; i++) {
            const pos = i / width;
            context.fillStyle = (zoom_interval[0] <= pos && zoom_interval[1] >= pos) ? d3.interpolateTurbo(pos) : "#eeeeee";
            context.fillRect(i, 0, 1, height);
        }

        context.fillStyle = '#1a237e';
        context.globalAlpha = 0.6
        for (const interval of intervals) {
           context.fillRect(interval[0] * width, 0, (interval[1] - interval[0]) * width, height);
        }

    }

    onMount(() => {
        context = canvas.getContext('2d');
        render(zoom_interval, intervals)
    })

    $: render(zoom_interval, intervals);
</script>

<div class="w-full">
    <canvas {height} {width} bind:this={canvas}></canvas>
</div>
