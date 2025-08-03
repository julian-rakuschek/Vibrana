<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import {onMount} from "svelte";
    import FingerprintRendering from "@components/atoms/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";

    export let width: number;
    export let index_allocation: number[];
    export let fingerprints: Fingerprint[];
    export let colorMapping: ClusterColorMapping;
    export let dataProvider: DataProvider;
    let loading = dataProvider.loading;

    const size: number = 100;
    const fingerprints_count: number = Math.max(0, Math.floor(width / size));

    let divRefs: HTMLDivElement[] = Array(fingerprints_count);
    let parentDiv: HTMLDivElement;
    let xPositions: number[] = [];
    let fingerprint_index_allocation: number[] = Array(fingerprints_count).fill(-1);

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

    function choose_fingerprint_indices(index_allocation: number[]) {
        if (!parentDiv) return;
        const base_left = parentDiv.getBoundingClientRect().left
        xPositions = divRefs.map(div => div.getBoundingClientRect().left - base_left);
        for (let i = 0; i < fingerprints_count; i++) {
            if (fingerprint_index_allocation[i] === -1) {
                const x_position = Math.floor(xPositions[i] + size / 2);
                const x_lower = Math.floor(xPositions[i]);
                const x_upper = Math.floor(xPositions[i] + size);
                fingerprint_index_allocation[i] = get_nearest_fingerprint(x_position, x_lower, x_upper, index_allocation);
            }
        }
    }



    onMount(() => {
        choose_fingerprint_indices(index_allocation);
    });

    $: choose_fingerprint_indices(index_allocation);


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
                     style={`background-color: ${colorMapping[fp.label]}`}></div>
                <div class="absolute">
                    {#if $loading}
                        <CenteredLoadingSpinner/>
                    {:else}
                        <FingerprintRendering
                                {dataProvider} {size}
                                update_on_fp_change={false}
                                transparent
                                fingerprint={fp}
                        />
                    {/if}
                </div>
            {/if}
        </div>
    {/each}
</div>
