<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";

    import {page} from '$app/stores';
    import type {DatasetConfig} from "@lib/types";
    import DatasetListItem from "@components/lists/DatasetListItem.svelte";
    import WIP from "@components/atoms/WIP.svelte";

    const datasets = $page.data.config

    const datasets_by_task: { [task: string]: string[] } = {
        large_signals: Object.keys(datasets).filter(d => datasets[d].chunks_or_stream_or_large === "large"),
        chunks: Object.keys(datasets).filter(d => datasets[d].chunks_or_stream_or_large === "chunks"),
        streams: Object.keys(datasets).filter(d => datasets[d].chunks_or_stream_or_large === "stream"),
    }

</script>

<div class="w-full grid grid-cols-3 gap-4 justify-center items-center h-full p-20 font-[Poppins] bg-[#faf9f5]">
    <div class="flex px-10 flex-col rounded-2xl border-2 border-[#1F1E1D20] bg-white h-full overflow-y-scroll">
        <div class="py-5 border-b-[1px] border-b-gray-900/40">
            <p class="text-xl font-bold">Large Signal Analysis</p>
            <p class="text-sm">Analyze a large signal, which may not fit into memory, using techniques from progressive
                data analysis to iteratively compute and cluster vibration fingerprints.</p>
        </div>
        {#each datasets_by_task.large_signals as large_signal}
            <DatasetListItem dataset={datasets[large_signal]} dataset_key={large_signal} />
        {/each}
    </div>
    <div class="flex px-10 flex-col rounded-2xl border-2 border-[#1F1E1D20] bg-white h-full overflow-y-scroll">
        <div class="py-5 border-b-[1px] border-b-gray-900/40">
            <p class="text-xl font-bold">Chunk Analysis</p>
            <p class="text-sm">Compare self-contained vibrations with each other via clustering.</p>
        </div>
        <WIP />
    </div>
    <div class="flex px-10 flex-col rounded-2xl border-2 border-[#1F1E1D20] bg-white h-full overflow-y-scroll">
        <div class="py-5 border-b-[1px] border-b-gray-900/40">
            <p class="text-xl font-bold">Stream Analysis</p>
            <p class="text-sm">Observe incoming streams of vibrations and observe how the fingerprint changes over tiem and thus reveals underlying changes in the vibration.</p>
        </div>
        <WIP />
    </div>
</div>


