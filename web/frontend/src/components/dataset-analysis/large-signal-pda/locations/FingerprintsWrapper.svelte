<script lang="ts">

    import FingerprintHover from "@components/dataset-analysis/large-signal-pda/locations/FingerprintHover.svelte";
    import IntervalSelection from "@components/dataset-analysis/large-signal-pda/locations/IntervalSelection.svelte";
    import FingerprintLocations
        from "@components/dataset-analysis/large-signal-pda/locations/FingerprintLocations.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import type {Fingerprint} from "@lib/types";

    export let dataset: string;
    export let subset: string;
    export let index_allocation: number[] = [];
    export let colors: string[] = [];
    export let width = 1000;
    export let dataProvider: DataProvider;
    export let fingerprints: Fingerprint[] = [];
    let mouse_x = -1;
</script>

<div class="w-full relative h-[100px]">
    <div class="w-full absolute top-0 left-0">
        <FingerprintLocations {width} {dataset} {subset} {index_allocation} {colors}/>
    </div>
    <div class="w-full absolute top-0 left-0">
        <IntervalSelection {width} {dataset} {subset} bind:mouse_x/>
    </div>
    <div class="w-full absolute top-[100px] left-0">
        <FingerprintHover {width} {fingerprints} {index_allocation} {dataProvider} {mouse_x}/>
    </div>
</div>