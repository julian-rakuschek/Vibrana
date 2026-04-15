<script lang="ts">
    import type {ClusterColorMapping, Fingerprint, Point} from "@lib/types";
    import {onMount, untrack} from "svelte";
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

    const size = 100;
    const connectorHeight = 30;
    const fingerprints_count = Math.max(0, Math.floor(width / size));

    let divRefs: HTMLDivElement[] = $state(Array(fingerprints_count));
    let parentDiv: HTMLDivElement = $state();
    let fingerprint_index_allocation: (Fingerprint | null)[] = $state(Array(fingerprints_count).fill(null));

    function get_nearest_fingerprint(
        x_position: number,
        lower_bound: number,
        upper_bound: number,
        index_allocation: number[],
        fingerprints: Fingerprint[]
    ): Fingerprint | null {
        if (x_position >= index_allocation.length || x_position < 0) return null;
        let step = 0;
        while (step < index_allocation.length) {
            const left = x_position - step >= 0 ? x_position - step : 0;
            const right = x_position + step < index_allocation.length ? x_position + step : index_allocation.length - 1;
            if (index_allocation[left] !== -1 && left >= lower_bound) return fingerprints[index_allocation[left]];
            if (index_allocation[right] !== -1 && right <= upper_bound) return fingerprints[index_allocation[right]];
            if (left < lower_bound && right > upper_bound) break;
            step++;
        }
        return null;
    }

    function getDivPositions() {
        const base_left = parentDiv.getBoundingClientRect().left;
        return divRefs.map(div => div.getBoundingClientRect().left - base_left);
    }

    function computeFingerprintIndices(index_allocation: number[], fingerprints: Fingerprint[]) {
        if (!parentDiv) return Array(fingerprints_count).fill(null);

        const xPositions = getDivPositions();

        return Array.from({ length: fingerprints_count }, (_, i) => {
            const x_position = Math.floor(xPositions[i] + size / 2);
            const x_lower = Math.floor(xPositions[i]);
            const x_upper = Math.floor(xPositions[i] + size);
            return get_nearest_fingerprint(x_position, x_lower, x_upper, index_allocation, fingerprints);
        });
    }

    export function choose_fingerprint_indices(
        index_allocation: number[],
        updateAllFingerprints: boolean,
        fingerprints: Fingerprint[]
    ) {
        if (updateAllFingerprints) {
            fingerprint_index_allocation = computeFingerprintIndices(index_allocation, fingerprints);
            return;
        }

        const previous = untrack(() => fingerprint_index_allocation);
        fingerprint_index_allocation = previous.map(fp =>
            fp ? fingerprints[fp.index] : null
        );
    }

    function generateConnectionLines(fingerprint_index_allocation: (Fingerprint | null)[], feature: "tde" | "psd") {
        if (!parentDiv) return [];
        const xPositions = getDivPositions();
        const lines = [];
        const linkGenerator = d3.linkVertical().x((d: Point) => d.x).y((d: Point) => d.y);

        for (let i = 0; i < fingerprints_count; i++) {
            const fp = fingerprint_index_allocation[i];
            if (fp) {
                const source: Point = {x: Math.floor(xPositions[i] + size / 2), y: 0};
                const fp_x_start = fp.start_index / fp.max_index;
                const fp_x_end = fp_x_start + fp.slice_length / fp.max_index;
                const fp_target = (fp_x_start + fp_x_end) / 2;
                const zoomed = (fp_target - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
                const target: Point = {x: Math.floor(zoomed * width), y: connectorHeight};

                lines.push({
                    d: linkGenerator({source, target}),
                    color: colorMapping[fp.label[feature]]
                });
            }
        }

        return lines;
    }

    onMount(() => {
        fingerprint_index_allocation = computeFingerprintIndices(index_allocation, fingerprints);
    });

    $effect(() => {
        zoom_interval;
        index_allocation;
        fingerprints;
        if (!parentDiv) return;
        fingerprint_index_allocation = computeFingerprintIndices(index_allocation, fingerprints);
    });
</script>

<div class="flex flex-row justify-between" bind:this={parentDiv}>
    {#each {length: fingerprints_count} as _, i}
        <div
                class="bg-white rounded-3xl shrink-0 relative"
                style={`height: ${size}px; width: ${size}px`}
                bind:this={divRefs[i]}
        >
            {#if fingerprint_index_allocation[i]}
                <div class="absolute opacity-15 w-full h-full  rounded-3xl"
                     style={`background-color: ${colorMapping[fingerprint_index_allocation[i].label[$fingerprintMode]]}`}></div>
                <div class="absolute w-full h-full">
                    {#if $loading}
                        <CenteredLoadingSpinner color={colorMapping[fingerprint_index_allocation[i].label[$fingerprintMode]]} />
                    {:else}
                        {#if $fingerprintMode === "tde"}
                            <FingerprintRendering
                                    {dataProvider} {size}
                                    cache_projection={true}
                                    transparent
                                    fingerprint={$state.snapshot(fingerprint_index_allocation[i])}
                                    color={colorMapping[fingerprint_index_allocation[i].label[$fingerprintMode]]}
                            />
                        {:else}
                            <PSDRendering size={size} frequencies={fingerprint_index_allocation[i].feature_descriptors.psd.f} power={fingerprint_index_allocation[i].feature_descriptors.psd.Pxx_spec}  color={colorMapping[fingerprint_index_allocation[i].label.psd]} />
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
