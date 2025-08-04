<script lang="ts">
    import AreaSelection from "@components/demos/AreaSelection.svelte";
    import Navbar from "@components/manage/Navbar.svelte";
    import MouseButtonRight from "@components/icons/MouseButtonRight.svelte";
    import MouseButtonLeft from "@components/icons/MouseButtonLeft.svelte";
    import MouseScroll from "@components/icons/MouseScroll.svelte";
    import AreaSelectionZoomIndicator from "@components/demos/AreaSelectionZoomIndicator.svelte";

    let zoom_interval: [number, number] = [0, 1];
    let intervals: [number, number][] = [];
    let width = 1000;

    function resetIntervals() {
        intervals = [];
    }
</script>

<Navbar/>
<div class="p-10">
    <p class="text-2xl">Interval Selection & Zooming Demo</p>
    <div class="flex flex-col mt-2">
        <div class="flex flex-row items-center text-black/70 text-md">
            <MouseButtonLeft/>
            & drag: Add Interval
        </div>
        <div class="flex flex-row items-center text-black/70 text-md">
            <MouseButtonRight/>
            & drag: Remove (Partial) Interval
        </div>
        <div class="flex flex-row items-center text-black/70 text-md">
            <MouseScroll/>
            : Zoom
        </div>
    </div>
    <p class="mt-4">Define intervals in this area (also allows zooming):</p>
    <AreaSelection {width} bind:zoom_interval bind:intervals/>
    <div class="flex">
        <p on:click={resetIntervals}
           class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">
            Reset intervals</p>
    </div>
    <p class="mt-4">Zoom Indicator:</p>
    <AreaSelectionZoomIndicator {zoom_interval} {intervals} {width}/>
</div>

