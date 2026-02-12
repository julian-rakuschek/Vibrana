<script lang="ts">
    import {humanTimeSpan} from "@lib/helper/util.js";
    import Icon from '@iconify/svelte';

    interface Props {
        timestamps: number[];
    }

    let { timestamps }: Props = $props();
</script>

<div class="gap-2 flex flex-col pb-3">
    <p class="font-semibold">Fingerprint Locations and Clusters</p>
    <p class="text-sm">
        The visualization shows the location of computed fingerprints across the signal.
        Each fingerprint is assigned to a cluster, which is shown through the colors.
        Since the algorithm computes one fingerprint at a time, users may steer the algorithm by defining
        intervals.
        The algorithm will subsequently only compute fingerprints in defined intervals.
        If no interval is defined, a random index is sampled.
        For large signals, users may zoom into the signal.
    </p>
    <div class="flex flex-col px-3">
        <div class="flex flex-row items-center text-black/70 text-md">
            <Icon icon="iconoir:mouse-button-left" />
            & drag: Add Interval
        </div>
        <div class="flex flex-row items-center text-black/70 text-md">
            <Icon icon="iconoir:mouse-button-right" />
            & drag: Remove (Partial) Interval
        </div>
        <div class="flex flex-row items-center text-black/70 text-md">
            <Icon icon="iconoir:mouse-scroll-wheel" />
            : Zoom
        </div>
    </div>
    <p class="text-center italic"><span
            class="font-semibold text-indigo-700">Time Span:</span> {humanTimeSpan(timestamps)}</p>
</div>