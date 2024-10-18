<script lang="ts">
	import {getContext} from "svelte";

	const { ro } = getContext("ro") as {ro: boolean}
</script>

<div class="grow flex flex-col items-center justify-center mt-20">
	<img width={400} alt="" src="/vibrana.png" />
	<p class="text-[#1c2934] text-6xl font-bold">Vibrana</p>
	<p class="text-[#1c2934] text-xl">Analyze and Annotate Vibration Signals Easily</p>
	{#if ro}
        <div class="bg-red-700 text-white rounded-lg p-4 w-[500px] text-sm">
            This demo is in <b>read-only mode</b>: Any changes will be saved in the browser and will be gone once the browser is closed.
            Download the docker-compose setup to work with your own data.
        </div>
    {/if}
</div>
