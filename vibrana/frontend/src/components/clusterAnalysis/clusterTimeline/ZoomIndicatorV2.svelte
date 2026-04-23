<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import {computeLabelAllocationArray, computeVisibleIndices} from "@lib/helper/fingerprintHelper";
    import {AVLTree} from "avl";
    import type IntervalTree from "node-interval-tree";
    import TimelineSegmentationVisualization
        from "@components/clusterAnalysis/clusterTimeline/TimelineSegmentationVisualization.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";

    interface Props {
        width?: number;
        zoom_interval?: [number, number];
        colorMapping: ClusterColorMapping;
        reset_zoom: () => void;
        fp_tree: AVLTree<number, Fingerprint>;
        fp_interval_tree: IntervalTree<Fingerprint>;
        dataProvider: DataProvider;
    }

    let {
        width = 1000,
        zoom_interval = [0, 1],
        colorMapping,
        reset_zoom,
        fp_tree,
        fp_interval_tree,
        dataProvider
    }: Props = $props();

</script>
<p class="text-sm"><b>You are here:</b> (the blue box shows the currently visible area)</p>
<div class="w-full relative h-[30px]">
    <div class="w-full absolute top-0 left-0">
        {#await dataProvider.get_length() then len}
            <TimelineSegmentationVisualization bar_height_based_on_density={false} height={30} {width} {colorMapping} {fp_tree} {fp_interval_tree} visibleIndices={computeVisibleIndices([0, 1], width, len)}/>
        {/await}
    </div>
    <div class="absolute w-[50%] h-full border-2 border-solid border-indigo-800 bg-indigo-700/30" style="width: {(zoom_interval[1] - zoom_interval[0]) * width}px; left: {zoom_interval[0] * width}px">

    </div>
</div>

<div class="flex flex-row justify-center">
    <button onclick={() => reset_zoom()} class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">Reset Zoom</button>
</div>
