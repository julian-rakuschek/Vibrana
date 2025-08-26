<script lang="ts">
    import {onMount} from 'svelte';
    import type {Fingerprint} from '@lib/types';
    import {indexListForDensityPlot, computeIndexAllocationArray} from "@lib/helper/fingerprintHelper";
    import { density1d } from 'fast-kde';
    import * as d3 from "d3";

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[];
    export let zoom_interval: [number, number] = [0, 1];

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 200;
    let indices: number[] = [];
    let aging: number[] = [];

    function render() {
        if (!context) return;
				context.clearRect(0, 0, width, height);
        const max = aging.toSorted((a, b) => a - b)[aging.length - 1];
        const min = -1;
        const colorScale = d3.scaleSequential(d3.interpolateViridis).domain([min, max === -1 ? 1 : max]);
        const density = density1d(indices, {bins: width, extent: [0, width], bandwidth: 10})
        let densities = density.grid();
        let max_density = densities.toSorted((a, b) => a - b)[densities.length - 1];
        densities = densities.map(d => d / max_density)
        for (let i = 0; i < width; i++) {
            const pos = i / width;
            context.fillStyle = (zoom_interval[0] <= pos && zoom_interval[1] >= pos) ? colorScale(aging[i]) : "#eeeeee";
            context.fillRect(i, height, 1, -height * densities[i]);
        }
    }

    function updateProcedure(fingerprints: Fingerprint[], width: number, zoom_interval: [number, number]) {
        indices = indexListForDensityPlot(fingerprints, width);
        aging = computeIndexAllocationArray(fingerprints, width, [0, 1]);
        render();
    }

    onMount(() => {
        context = canvas.getContext('2d');
        updateProcedure(fingerprints, width, zoom_interval);
    })

    $: updateProcedure(fingerprints, width, zoom_interval);
</script>

<canvas bind:this={canvas} width={width} height={height}></canvas>