<script lang="ts">
    import {onMount} from 'svelte';
    import {ColorMode, type Fingerprint} from '@lib/types';
    import {indexListForDensityPlot, computeIndexAllocationArray} from "@lib/helper/fingerprintHelper";
    import {density1d} from 'fast-kde';
    import * as d3 from "d3";
    import ColorLegend from "@components/atoms/ColorLegend.svelte";


    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    interface Props {
        dataset: string;
        subset: string;
        fingerprints: Fingerprint[];
        zoom_interval?: [number, number];
        width?: number;
    }

    let {
        dataset,
        subset,
        fingerprints,
        zoom_interval = [0, 1],
        width = 1000
    }: Props = $props();
    const height = 100;
    let indices: number[] = [];

    function render() {
        if (!context) return;
        context.clearRect(0, 0, width, height);
        const colorScale = d3.scaleSequential(d3.interpolateViridis);
        const density = density1d(indices, {bins: width, extent: [0, width], bandwidth: 50})
        let densities = density.grid();
        let max_density = densities.toSorted((a, b) => a - b)[densities.length - 1];
        densities = densities.map(d => d / max_density)
        for (let i = 0; i < width; i++) {
            context.fillStyle = colorScale(1 - densities[i]);
            context.fillRect(i, height, 1, -height * (1 - densities[i]));
        }
    }

    function updateProcedure(fingerprints: Fingerprint[], width: number, zoom_interval: [number, number]) {
        indices = indexListForDensityPlot(fingerprints, width, zoom_interval);
        render();
    }

    onMount(() => {
        context = canvas.getContext('2d');
        updateProcedure(fingerprints, width, zoom_interval);
    })

    $effect(() => {
        updateProcedure(fingerprints, width, zoom_interval);
    });
</script>

<div class="w-full flex flex-row justify-between px-10 mb-4">
    <p class="font-semibold mt-5 mb-2">Uncertainty</p>
    <div class="w-[500px]">
        <ColorLegend colorMode={ColorMode.Uncertainty}/>
    </div>
</div>
<canvas bind:this={canvas} width={width} height={height}></canvas>