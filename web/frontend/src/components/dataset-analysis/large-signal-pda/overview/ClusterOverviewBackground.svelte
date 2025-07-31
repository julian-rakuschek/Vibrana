<script lang="ts">
    import type {ClusterColorMapping, ClusterOverviewSector, Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {computeIndexAllocationArray} from "@lib/helper/fingerprintHelper";
    import {fillGaps} from "@lib/algorithms/gapFill";

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[] = [];
    export let colorMapping: ClusterColorMapping;
    export let dataProvider: DataProvider;
    let loading = dataProvider.loading;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 100;
    let labelAllocation: number[] = [];

    function render() {
        if (!context) return;
        context.clearRect(0, 0, width, height);
        context.fillStyle = '#FFFFFF';
        context.fillRect(0, 0, width, height);
        if (labelAllocation.length !== width) return;
        const filledGaps = fillGaps(labelAllocation, null);
        if (filledGaps[0] === null) return;
        for (let i = 0; i < width; i++) {
            const label = filledGaps[i];
            context.globalAlpha = 0.2;
            context.fillStyle = label === null ? "lightgray" : colorMapping[label];
            context.fillRect(i, 0, 1, height);
        }
    }

    function updateProcedure(fingerprints: Fingerprint[]) {
        labelAllocation = computeIndexAllocationArray(fingerprints, width, null, true);
        render();
    }

    onMount(async () => {
        context = canvas.getContext('2d');
        updateProcedure(fingerprints)
    })

    loading.subscribe(() => {
        updateProcedure(fingerprints)
    })

    $: {
        updateProcedure(fingerprints)
    }
</script>

<div class="w-full">
    <canvas {height} {width} bind:this={canvas}></canvas>
</div>