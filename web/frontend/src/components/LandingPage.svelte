<script lang="ts">
    import {getContext} from "svelte";

    const {ro} = getContext("ro") as { ro: boolean }
</script>

<div class="grow flex flex-col items-center justify-center">
    {#if ro}
        <div class="bg-[#304ffe] text-white rounded-lg p-4 w-[500px] text-sm mb-10">
            This demo is in <b>read-only mode</b>: Any changes will be saved in the browser and will be gone once page is reloaded.
            Download the docker-compose setup to work with your own data (available in the near future).
        </div>
    {/if}
    <img width={300} alt="" src="/vibrana.png"/>
    <p class="text-[#1c2934] text-6xl font-bold">Vibrana</p>
    <p class="text-[#1c2934] text-xl">A tool for exploring and annotating vibration signals through a different perspective</p>
    <div class="flex flex-col mt-10 gap-5">
        <a class="rounded-md text-center bg-[#1c2934] px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-[#121a21]" href="/intro">How to use Vibrana</a>
        <a class="rounded-md text-center bg-[#1c2934] px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-[#121a21]" href="/datasets">Explore Datasets</a>
        <a class="rounded-md text-center bg-[#1c2934] px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-[#121a21]" href="/authors">Authors</a>
    </div>
</div>
