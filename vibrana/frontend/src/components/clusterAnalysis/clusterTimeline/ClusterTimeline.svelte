<script lang="ts">

    import FingerprintHover from "@components/clusterAnalysis/clusterTimeline/FingerprintHover.svelte";
    import FingerprintLocations
        from "@components/clusterAnalysis/clusterTimeline/FingerprintLocations.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {type ClusterColorMapping, type Fingerprint} from '@lib/types';
    import ClusterBackground from '@components/clusterAnalysis/clusterTimeline/ClusterBackground.svelte';
    import TimestampHover from "@components/clusterAnalysis/clusterTimeline/TimestampHover.svelte";
    import {formatUnixTimestamp} from "@lib/helper/util";
    import IntervalSelection from "@components/clusterAnalysis/clusterTimeline/IntervalSelection.svelte";
    import {AVLTree} from "avl";
    import {computeVisibleIndices} from "@lib/helper/fingerprintHelper";

    interface Props {
        dataset: string;
        subset: string;
        index_allocation?: number[];
        label_allocation?: number[];
        width?: number;
        dataProvider: DataProvider;
        fp_tree: AVLTree<number, Fingerprint>;
        fingerprints?: Fingerprint[];
        colorMapping: ClusterColorMapping;
        zoom_interval?: [number, number];
        timestamps?: number[];
    }

    let {
        dataset,
        subset,
        index_allocation = [],
        label_allocation = [],
        width = 1000,
        dataProvider,
        fp_tree,
        fingerprints = [],
        colorMapping,
        zoom_interval = $bindable([0, 1]),
        timestamps = []
    }: Props = $props();
    let intervalSelector: IntervalSelection = $state();
    let mouse_x = $state(-1);

    function resetIntervals() {
        if (!intervalSelector) return;
        intervalSelector.resetIntervals();
    }
</script>

<div class="w-full relative h-[100px]">
    <div class="w-full absolute top-0 left-0">
        <ClusterBackground {width} {colorMapping} {fp_tree} visibleIndices={computeVisibleIndices(zoom_interval, width, dataProvider.get_length())} />
    </div>
    <div class="w-full absolute top-0 left-0">
        <FingerprintLocations {width} {label_allocation} {colorMapping} />
    </div>
    <div class="w-full absolute top-0 left-0">
        <IntervalSelection {width} {dataset} {subset} bind:mouse_x bind:this={intervalSelector} bind:zoom_interval />
    </div>
    <div class="w-full absolute top-[100px] left-0">
        <FingerprintHover {width} {fingerprints} {index_allocation} {dataProvider} {mouse_x} />
    </div>
    <div class="w-full absolute top-[-50px] left-0">
        <TimestampHover {width} {mouse_x} {timestamps} />
    </div>
    <div class="w-[100px] absolute top-1/2 -translate-y-1/2 -left-[70px] rotate-90">
        {#if timestamps.length > 0}
            <p class="text-center text-xs">{formatUnixTimestamp(timestamps[0]).isoDate}</p>
            <p class="text-center text-sm">{formatUnixTimestamp(timestamps[0]).time}</p>
        {/if}
    </div>
    <div class="w-[100px] absolute top-1/2 -translate-y-1/2 -right-[70px] rotate-90">
        {#if timestamps.length > 0}
            <p class="text-center text-xs">{formatUnixTimestamp(timestamps[timestamps.length - 1]).isoDate}</p>
            <p class="text-center text-sm">{formatUnixTimestamp(timestamps[timestamps.length - 1]).time}</p>
        {/if}
    </div>
</div>
<div class="flex">
    <p onclick={resetIntervals} class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">Reset intervals</p>
</div>
