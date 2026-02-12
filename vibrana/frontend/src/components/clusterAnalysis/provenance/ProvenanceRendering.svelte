<script lang="ts">
    import type {ClusterColorMapping, Provenance, ProvenanceSeed} from "@lib/types";
    import {onMount, tick} from "svelte";
    import {fillGaps} from "@lib/algorithms/gapFill";
    import {ColorGenerator} from "@lib/algorithms/colorGenerator";

    interface Props {
        provenance_records?: Provenance[];
        width?: number;
        feature: string;
    }

    let { provenance_records = [], width = 1000, feature }: Props = $props();

    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    let colorGenerator: ColorGenerator = new ColorGenerator();
    const rowHeight = 10;
    let height = $derived(provenance_records.length * rowHeight);

    function breakpointsToStripe(seeds: ProvenanceSeed[], signal_length: number, width: number) {
        let label_allocation: number[] = new Array(width).fill(null);
        for (const seed of seeds) {
            const idx = Math.floor(seed.index / signal_length * width);
            label_allocation[idx] = seed.label;
        }
        return fillGaps(label_allocation, null);
    }

    function render(provenance_records: Provenance[]) {
        if (!context) return;
        context.clearRect(0, 0, width, height);
        context.fillStyle = '#FFFFFF';
        context.fillRect(0, 0, width, height);
        for (let i = 0; i < provenance_records.length; i++) {
            const labels = breakpointsToStripe(provenance_records[i].breakpoints[feature], provenance_records[i].signal_length, width);
            for (let j = 0; j < width; j++) {
                const label = labels[j];
                context.globalAlpha = 1;
                context.fillStyle = label === null ? 'lightgray' : colorGenerator.getColor(label);
                context.fillRect(j, rowHeight * i, 1, rowHeight);
            }
        }
    }

    async function init(provenance_records: Provenance[], height: number) {
        context = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;
        await tick()
        render(provenance_records);
    }

    onMount(async () => {
        init(provenance_records, height)
    });

    $effect(() => {
        init(provenance_records, height)
    });
</script>

<div>
    {#if feature === "tde"}
        <p class="text-center italic">Projection</p>
    {:else}
        <p class="text-center italic">PSD</p>
    {/if}
    <canvas bind:this={canvas}></canvas>
</div>