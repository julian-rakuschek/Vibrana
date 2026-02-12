<script lang="ts">
    import type {ClusterColorMapping, Fingerprint, Point} from "@lib/types";
    import {onMount} from "svelte";
    import FingerprintRendering from "@components/fingerprintRenderer/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import * as d3 from 'd3';
    import {fingerprintMode} from "@lib/stores";
    import PSDRendering from "@components/fingerprintRenderer/PSDRendering.svelte";

    interface Props {
        width: number;
        index_allocation: number[];
        zoom_interval?: [number, number];
        fingerprints: Fingerprint[];
        colorMapping: ClusterColorMapping;
        dataProvider: DataProvider;
    }

    let {
        width,
        index_allocation,
        zoom_interval = [0, 1],
        fingerprints,
        colorMapping,
        dataProvider
    }: Props = $props();
    let loading = dataProvider.loading;

    const size: number = 100;
    const connectorHeight: number = 30;
    const fingerprints_count: number = Math.max(0, Math.floor(width / size));

    let divRefs: HTMLDivElement[] = $state(Array(fingerprints_count));
    let parentDiv: HTMLDivElement = $state();
    let fingerprint_index_allocation: number[] = $state(Array(fingerprints_count).fill(-1));

    let timeoutId: ReturnType<typeof setTimeout>;

    function handleZoom(zoom_interval: [number, number]) {
        clearTimeout(timeoutId);
        fingerprint_index_allocation = Array(fingerprints_count).fill(-1);
        timeoutId = setTimeout(() => {
            choose_fingerprint_indices(index_allocation, true);
        }, 500);
    }

    function get_nearest_fingerprint(x_position: number, lower_bound: number, upper_bound: number, index_allocation: number[]) {
        if (x_position >= index_allocation.length || x_position < 0) return -1;
        let step = 0;
        while (step < index_allocation.length) {
            const left = x_position - step >= 0 ? x_position - step : 0;
            const right = x_position + step < index_allocation.length ? x_position + step : index_allocation.length - 1;
            if (index_allocation[left] !== -1 && left >= lower_bound) return index_allocation[left];
            if (index_allocation[right] !== -1 && right <= upper_bound) return index_allocation[right];
            if (left < lower_bound && right > upper_bound) break;
            step++;
        }
        return -1;
    }

    function getDivPositions() {
        const base_left = parentDiv.getBoundingClientRect().left
        return divRefs.map(div => div.getBoundingClientRect().left - base_left);
    }

    function choose_fingerprint_indices(index_allocation: number[], updateAllFingerprints: boolean) {
        if (!parentDiv) return;
        const xPositions = getDivPositions();
        for (let i = 0; i < fingerprints_count; i++) {
            if (fingerprint_index_allocation[i] === -1 || updateAllFingerprints) {
                const x_position = Math.floor(xPositions[i] + size / 2);
                const x_lower = Math.floor(xPositions[i]);
                const x_upper = Math.floor(xPositions[i] + size);
                fingerprint_index_allocation[i] = get_nearest_fingerprint(x_position, x_lower, x_upper, index_allocation);
            }
        }
    }

    function generateConnectionLines(fingerprint_index_allocation: number[], feature: "tde" | "psd") {
        if (!parentDiv) return [];
        const xPositions = getDivPositions();
        const lines = [];
        const linkGenerator = d3.linkVertical().x((d: Point) => d.x).y((d: Point) => d.y);
        for (let i = 0; i < fingerprints_count; i++) {
            if (fingerprint_index_allocation[i] !== -1) {
                const fp = fingerprints[fingerprint_index_allocation[i]];
                const source: Point = {x: Math.floor(xPositions[i] + size / 2), y: 0};
                const fp_x_start = (fp.start_index / fp.max_index);
                const fp_x_end = fp_x_start + (fp.slice_length / fp.max_index);
                const fp_target = (fp_x_start + fp_x_end) / 2;
                const zoomed = (fp_target - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
                const target: Point = {x: Math.floor(zoomed * width), y: connectorHeight};
                lines.push({
                    d: linkGenerator({source, target}),
                    color: colorMapping[fp.label[feature]]
                })
            }
        }
        return lines;
    }


    onMount(() => {
        choose_fingerprint_indices(index_allocation, true);
    });

    $effect(() => {
        handleZoom(zoom_interval);
    });


</script>

<div class="flex flex-row justify-between" bind:this={parentDiv}>
    {#each {length: fingerprints_count} as _, i}
        <div
                class="bg-white rounded-3xl shrink-0 relative"
                style={`height: ${size}px; width: ${size}px`}
                bind:this={divRefs[i]}
        >
            {#if fingerprint_index_allocation[i] !== -1}
                {@const fp = fingerprints[fingerprint_index_allocation[i]]}
                <div class="absolute opacity-15 w-full h-full  rounded-3xl"
                     style={`background-color: ${colorMapping[fp.label[$fingerprintMode]]}`}></div>
                <div class="absolute w-full h-full">
                    {#if $loading}
                        <CenteredLoadingSpinner color={colorMapping[fp.label[$fingerprintMode]]} />
                    {:else}
                        {#if $fingerprintMode === "tde"}
                            <FingerprintRendering
                                    {dataProvider} {size}
                                    update_on_fp_change={false}
                                    transparent
                                    fingerprint={fp}
                                    color={colorMapping[fp.label[$fingerprintMode]]}
                            />
                        {:else}
                            <PSDRendering size={size} frequencies={fp.feature_descriptors.psd.f} power={fp.feature_descriptors.psd.Pxx_spec}  color={colorMapping[fp.label.psd]} />
                        {/if}
                    {/if}
                </div>
            {/if}
        </div>
    {/each}
</div>

<div class="w-full">
    <svg width={width} height={connectorHeight}>
        {#each generateConnectionLines(fingerprint_index_allocation, $fingerprintMode) as path}
            <path d={path.d} fill="none" stroke={path.color} stroke-width={2}/>
        {/each}
    </svg>
</div>
