<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import {computeVisibleIndices} from "@lib/helper/fingerprintHelper";
    import {AVLTree} from "avl";
    import type IntervalTree from "node-interval-tree";
    import TimelineSegmentationVisualization
        from "@components/clusterAnalysis/clusterTimeline/TimelineSegmentationVisualization.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {brushSelection, brushX, select, type BrushBehavior, type D3BrushEvent} from "d3";

    interface Props {
        width?: number;
        zoom_interval?: [number, number];
        colorMapping: ClusterColorMapping;
        reset_zoom: () => void;
        fp_tree: AVLTree<number, Fingerprint>;
        fp_interval_tree: IntervalTree<Fingerprint>;
        dataProvider: DataProvider;
    }

    const height = 30;
    const minBrushWidthPx = 8;

    let {
        width = 1000,
        zoom_interval = $bindable([0, 1]),
        colorMapping,
        reset_zoom,
        fp_tree,
        fp_interval_tree,
        dataProvider
    }: Props = $props();

    let brushGroup: SVGGElement | undefined;
    let brushBehavior: BrushBehavior<SVGGElement> | undefined;

    function intervalToPixels(interval: [number, number]) {
        return [interval[0] * width, interval[1] * width] as [number, number];
    }

    function pixelsToInterval(selection: [number, number]) {
        const start = Math.max(0, Math.min(1, selection[0] / width));
        const end = Math.max(0, Math.min(1, selection[1] / width));
        return [Math.min(start, end), Math.max(start, end)] as [number, number];
    }

    function clampSelection(selection: [number, number]) {
        let [start, end] = selection;
        const minWidth = Math.min(width, minBrushWidthPx);

        if (end - start < minWidth) {
            const center = (start + end) / 2;
            start = center - minWidth / 2;
            end = center + minWidth / 2;
        }

        if (start < 0) {
            end -= start;
            start = 0;
        }

        if (end > width) {
            start -= end - width;
            end = width;
        }

        return [Math.max(0, start), Math.min(width, end)] as [number, number];
    }

    function sameSelection(a: [number, number] | null, b: [number, number]) {
        return a !== null && Math.abs(a[0] - b[0]) < 0.5 && Math.abs(a[1] - b[1]) < 0.5;
    }

    function syncBrushSelection() {
        if (!brushGroup || !brushBehavior) return;
        const targetSelection = clampSelection(intervalToPixels(zoom_interval));
        const currentSelection = brushSelection(brushGroup);
        if (sameSelection(currentSelection as [number, number] | null, targetSelection)) return;
        select(brushGroup).call(brushBehavior.move, targetSelection);
    }

    function initBrush() {
        if (!brushGroup) return;

        brushBehavior = brushX()
            .extent([[0, 0], [width, height]])
            .handleSize(10)
            .on("brush end", (event: D3BrushEvent<SVGGElement>) => {
                if (!event.selection || !event.sourceEvent) return;
                const clampedSelection = clampSelection(event.selection as [number, number]);
                if (!sameSelection(event.selection as [number, number], clampedSelection)) {
                    group.call(brushBehavior!.move, clampedSelection);
                    return;
                }
                zoom_interval = pixelsToInterval(clampedSelection);
            });

        const group = select(brushGroup);
        group.selectAll("*").remove();
        group.call(brushBehavior);
        group.select(".overlay").attr("cursor", "crosshair");
        group.select(".selection")
            .attr("fill", "#4338ca")
            .attr("fill-opacity", 0.25)
            .attr("stroke", "#312e81")
            .attr("stroke-width", 2);
        group.selectAll(".handle")
            .attr("fill", "#312e81")
            .attr("fill-opacity", 0.9);

        syncBrushSelection();
    }
    $effect(() => {
        if (!brushGroup || width <= 0) return;
        initBrush();
    });

    $effect(() => {
        zoom_interval;
        syncBrushSelection();
    });
</script>
<p class="text-sm"><b>You are here:</b> (the blue box shows the currently visible area)</p>
<div class="w-full relative h-[30px]">
    <div class="w-full absolute top-0 left-0">
        {#await dataProvider.get_length() then len}
            <TimelineSegmentationVisualization bar_height_based_on_density={false} {height} {width} {colorMapping} {fp_tree} {fp_interval_tree} visibleIndices={computeVisibleIndices([0, 1], width, len)}/>
        {/await}
    </div>
    <svg class="absolute top-0 left-0 overflow-visible zoom-brush" {width} {height}>
        <g bind:this={brushGroup}></g>
    </svg>
</div>

<div class="flex flex-row justify-center">
    <button onclick={() => reset_zoom()} class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">Reset Zoom</button>
</div>

<style>
    .zoom-brush :global(.overlay),
    .zoom-brush :global(.selection),
    .zoom-brush :global(.handle) {
        touch-action: none;
    }
    .zoom-brush :global(.selection) {
        cursor: move;
    }
    .zoom-brush :global(.handle) {
        cursor: ew-resize;
    }
</style>
