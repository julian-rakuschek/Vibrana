<script lang="ts">
    import {onMount} from "svelte";
    import {fillGaps} from "@lib/algorithms/gapFill";
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import {computeLabelAllocationArray} from "@lib/helper/fingerprintHelper";

    interface Props {
        width?: number;
        zoom_interval?: [number, number];
        intervals?: [number, number][];
        colorMapping: ClusterColorMapping;
        fingerprints: Fingerprint[];
        feature?: "tde" | "psd";
        reset_zoom: () => void;
    }

    let {
        width = 1000,
        zoom_interval = [0, 1],
        intervals = [],
        colorMapping,
        fingerprints,
        feature = "tde",
        reset_zoom
    }: Props = $props();

    const height = 20;
    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    let label_allocation: number[] = $state.raw([]);

    function render(zoom_interval: [number, number], intervals: [number, number][], label_allocation: number[]) {
        if (!context) return;
        context.globalAlpha = 1;
        context.fillStyle = '#eeeeee';
        context.fillRect(0, 0, width, height);
        const filledGaps = fillGaps(label_allocation, null);
        for (let i = 0; i < width; i++) {
            const pos = i / width;
            const label = filledGaps[i];
            context.fillStyle = (zoom_interval[0] <= pos && zoom_interval[1] >= pos && label !== null) ? colorMapping[label] : "#eeeeee";
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
        label_allocation = computeLabelAllocationArray(fingerprints, width, [0, 1], feature);
        render(zoom_interval, intervals, label_allocation)
    })

    $effect(() => {
        label_allocation = computeLabelAllocationArray(fingerprints, width, [0, 1], feature);
    });

    $effect(() => {
        render(zoom_interval, intervals, label_allocation);
    });
</script>

<p class="font-semibold mt-5 text-center">Zooming Location</p>
<div class="w-full">
    <canvas {height} {width} bind:this={canvas}></canvas>
</div>
<div class="flex flex-row justify-center">
    <button onclick={() => reset_zoom()} class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">Reset Zoom</button>
</div>
