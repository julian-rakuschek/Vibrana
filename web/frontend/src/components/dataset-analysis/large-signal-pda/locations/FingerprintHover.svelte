<script lang="ts">
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import FingerprintRendering from "@components/atoms/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import type {Fingerprint} from "@lib/types";

    export let dataProvider: DataProvider;
    let loading = dataProvider.loading;
    export let fingerprints: Fingerprint[] = [];
    export let width = 1000;
    export let mouse_x = -1;
    export let index_allocation: number[] = new Array(width).fill(-1);

    let hovering_fingerprint_index = -1;
    let hovering_fingerprint_pixel_pos = -1;

    function get_nearest_fingerprint(index: number) {
        if (index >= index_allocation.length || index < 0) return;
        let step = 0;
        hovering_fingerprint_index = -1;
        hovering_fingerprint_pixel_pos = -1;
        while (step < index_allocation.length) {
            const left = index - step >= 0 ? index - step : 0;
            const right = index + step < index_allocation.length ? index + step : index_allocation.length - 1;
            if (index_allocation[left] !== -1) {
                hovering_fingerprint_index = index_allocation[left];
                hovering_fingerprint_pixel_pos = left;
                break;
            }
            if (index_allocation[right] !== -1) {
                hovering_fingerprint_index = index_allocation[right];
                hovering_fingerprint_pixel_pos = right;
                break;
            }
            step++;
        }
    }

    $: get_nearest_fingerprint(Math.floor(mouse_x));
</script>

<div class="relative w-full" style={`width: ${width}px;`}>
    {#if mouse_x !== -1}
        <div class="absolute bg-indigo-800 w-[50px] h-[50px] -translate-x-1/2 rotate-45"
             style={`left: ${hovering_fingerprint_pixel_pos}px`}></div>
        <div class="absolute mt-3 p-3 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
             style={`left: ${hovering_fingerprint_pixel_pos}px`}>
            {#if $loading}
                <CenteredLoadingSpinner/>
            {:else}
                <FingerprintRendering {dataProvider} fingerprint={fingerprints[hovering_fingerprint_index]}/>
            {/if}
        </div>
    {/if}
</div>