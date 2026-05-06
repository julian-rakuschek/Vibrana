<script lang="ts">
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import FingerprintRendering from "@components/fingerprintRenderer/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import type {Fingerprint} from "@lib/types";
    import {fingerprintMode} from "@lib/stores";
    import FFTRendering from "@components/fingerprintRenderer/FFTRendering.svelte";

    interface Props {
        dataProvider: DataProvider;
        fingerprints?: Fingerprint[];
        width?: number;
        mouse_x?: any;
        index_allocation?: number[];
    }

    let {
        dataProvider,
        fingerprints = [],
        width = 1000,
        mouse_x = -1,
        index_allocation = new Array(width).fill(-1)
    }: Props = $props();

    const max_fp_mouse_distance = 20;

    let hovering_fingerprint_index = $state(-1);
    let hovering_fingerprint_pixel_pos = $state(-1);

    function get_nearest_fingerprint(index: number) {
        if (index >= index_allocation.length || index < 0) return;

        let foundIndex = -1;
        let foundPos = -1;

        let step = 0;
        while (step < index_allocation.length && step < max_fp_mouse_distance) {
            const left = index - step >= 0 ? index - step : 0;
            const right = index + step < index_allocation.length ? index + step : index_allocation.length - 1;

            if (index_allocation[left] !== -1) {
                foundIndex = index_allocation[left];
                foundPos = left;
                break;
            }
            if (index_allocation[right] !== -1) {
                foundIndex = index_allocation[right];
                foundPos = right;
                break;
            }
            step++;
        }

        // single commit (prevents false->true flicker)
        hovering_fingerprint_index = foundIndex;
        hovering_fingerprint_pixel_pos = foundPos;
    }


    let loading = dataProvider.loading;

    $effect(() => {
        get_nearest_fingerprint(Math.floor(mouse_x));
    });
</script>

<div class="relative w-full" style={`width: ${width}px;`}>
    {#if mouse_x !== -1 && hovering_fingerprint_index !== -1}
        <div class="absolute bg-indigo-800 w-[50px] h-[50px] -translate-x-1/2 rotate-45"
             style={`left: ${hovering_fingerprint_pixel_pos}px`}></div>
        <div class="absolute mt-3 p-3 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
             style={`left: ${hovering_fingerprint_pixel_pos}px`}>
            {#if $loading}
                <CenteredLoadingSpinner/>
            {:else}
                {#if $fingerprintMode === "tde"}
                    <FingerprintRendering {dataProvider} cache_projection={false} fingerprint={fingerprints[hovering_fingerprint_index]}/>
                {:else}
                    <FFTRendering
                            showAxis
                            frequencies={fingerprints[hovering_fingerprint_index].feature_descriptors.fft.f}
                            power={fingerprints[hovering_fingerprint_index].feature_descriptors.fft.magnitudes}
                    />
                {/if}
            {/if}
        </div>
    {/if}
</div>