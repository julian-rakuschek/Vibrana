<script lang="ts">

    import FingerprintHover from "@components/clusterAnalysis/clusterTimeline/FingerprintHover.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {type ClusterColorMapping, type Fingerprint, InteractionMode} from '@lib/types';
    import TimestampHover from "@components/clusterAnalysis/clusterTimeline/TimestampHover.svelte";
    import {formatUnixTimestamp} from "@lib/helper/util";
    import IntervalSelection from "@components/clusterAnalysis/clusterTimeline/IntervalSelection.svelte";
    import {AVLTree} from "avl";
    import {computeVisibleIndices} from "@lib/helper/fingerprintHelper";
    import TimelineSegmentationVisualization
        from "@components/clusterAnalysis/clusterTimeline/TimelineSegmentationVisualization.svelte";
    import type IntervalTree from "node-interval-tree";

    interface Props {
        dataset: string;
        subset: string;
        index_allocation?: number[];
        label_allocation?: number[];
        width?: number;
        dataProvider: DataProvider;
        fp_tree: AVLTree<number, Fingerprint>;
        fp_interval_tree: IntervalTree<Fingerprint>;
        fingerprints?: Fingerprint[];
        colorMapping: ClusterColorMapping;
        zoom_interval?: [number, number];
        timestamps?: number[];
        selectedIndices: number[];
    }

    let {
        dataset,
        subset,
        index_allocation = [],
        label_allocation = [],
        width = 1000,
        dataProvider,
        fp_tree,
        fp_interval_tree,
        fingerprints = [],
        colorMapping,
        zoom_interval = $bindable([0, 1]),
        timestamps = [],
        selectedIndices = $bindable([]),
    }: Props = $props();

    let intervalSelector: IntervalSelection = $state();
    let mouse_x = $state(-1);
    let interactionMode = $state(InteractionMode.SELECT);

    const inactive_button = "bg-white rounded-lg shadow-lg px-3 py-1 text-black cursor-default hover:bg-indigo-50"
    const active_button = "bg-indigo-500 text-white rounded-lg shadow-lg px-3 py-1 cursor-default"

    function resetIntervals() {
        if (!intervalSelector) return;
        intervalSelector.resetIntervals();
    }

    function resetSelectedIndices() {
        selectedIndices = [];
    }
</script>
<div class="flex w-full justify-center mb-2 gap-4">
    <div class="{interactionMode === InteractionMode.SELECT ? active_button : inactive_button}"
         onclick={() => interactionMode = InteractionMode.SELECT}>Sample Selection
    </div>
    <div class="{interactionMode === InteractionMode.INTERVAL ? active_button : inactive_button}"
         onclick={() => interactionMode = InteractionMode.INTERVAL}>Interval Definition
    </div>
</div>
<div class="flex w-full justify-center mb-10">
    {#if interactionMode === InteractionMode.SELECT}
        <p onclick={resetSelectedIndices}
           class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">
            Reset selected indices</p>
    {:else}
        <p onclick={resetIntervals}
           class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">
            Reset intervals</p>
    {/if}
</div>
<div class="w-full relative h-[100px]">

    <div class="w-full absolute top-0 left-0">
        {#await dataProvider.get_length() then len}
            <TimelineSegmentationVisualization {width} {colorMapping} {fp_tree} {fp_interval_tree}
                                               visibleIndices={computeVisibleIndices(zoom_interval, width, len)}/>
        {/await}
    </div>
    <div class="w-full absolute top-0 left-0">
        <IntervalSelection {width} {dataset} {subset} bind:mouse_x bind:this={intervalSelector} bind:zoom_interval
                           bind:selectedIndices interaction_mode={interactionMode}/>
    </div>
    <div class="w-full absolute top-[100px] left-0 z-50">
        <FingerprintHover {width} {fingerprints} {index_allocation} {dataProvider} {mouse_x}/>
    </div>
    <div class="w-full absolute top-[-50px] left-0">
        <TimestampHover {width} {mouse_x} {timestamps}/>
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

