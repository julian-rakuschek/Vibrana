<script lang="ts">
    import {
        Dialog,
        DialogOverlay,
        DialogTitle,
        DialogDescription,
    } from "@rgossiaux/svelte-headlessui";
    import WindowSizeSelector from "@components/charts/WindowSizeSelector.svelte";
    import {chartSettings} from "@lib/stores";

    export let isOpen = true;
    export let timeSeries: number[];
    let window: [number, number]

    const save = () => {
        const intervalSize = window[1] * timeSeries.length - window[0] * timeSeries.length;
        chartSettings.update(s => ({...s, windowSize: Math.floor(intervalSize)}))
        isOpen = false
    }
</script>

<Dialog open={isOpen} on:close={() => (isOpen = false)} class="z-10 fixed top-0 left-0 flex justify-center items-center w-full h-full">
    <DialogOverlay class="fixed top-0 left-0 bg-black/30 w-full h-full"/>
    <div class="z-10 bg-white rounded-lg p-4 flex flex-col items-center w-4/5">
        <p class="text-lg font-semibold">Select Interval Size</p>
        <p>Adjust the interval size using the chart below. Click and drag on the chart to select a window.</p>
        <div class="w-full">
            <WindowSizeSelector timeSeries={timeSeries} bind:window />
        </div>
        <button on:click={save} class="bg-indigo-500 text-white hover:bg-indigo-700 transition px-2 py-1 rounded-md mt-5">Done</button>
    </div>

</Dialog>