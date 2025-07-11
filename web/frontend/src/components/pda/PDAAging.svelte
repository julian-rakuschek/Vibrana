<script lang="ts">

    import {onMount} from "svelte";
    import {interpolateViridis} from "d3";

    export let aging: number[] = [];
    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null
    const width = 1000;
    const height = 20;

    function plotAging() {
        const max = aging.toSorted((a, b) => a - b)[aging.length - 1];
        const min = -1;
        
        if (!context) return;
        context.fillStyle = interpolateViridis(0);
        context.fillRect(0, 0, width, height)
        for (let i = 0; i < aging.length; i++) {
            const t = (aging[i] - min) / (max - min);
            context.fillStyle = interpolateViridis(t);
            context.fillRect(i, 0, 1, height)
        }
    }

    onMount(() => {
        context = canvas.getContext('2d')
        plotAging();
    });

    $: aging, plotAging();
</script>

<div>
    <canvas height={height} width={width} bind:this={canvas}></canvas>
</div>

