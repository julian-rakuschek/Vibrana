<script lang="ts">
    import {page} from '$app/stores';
    import DatasetListItem from "@components/lists/DatasetListItem.svelte";

    const datasets = $page.data.config

    console.log(datasets)

</script>

<div class="flex flex-col w-full gap-4 p-6 justify-center items-center h-full font-[Poppins] bg-[#faf9f5]">
    {#each Object.keys(datasets) as stream}
        <DatasetListItem dataset={datasets[stream]} dataset_key={stream} />
    {/each}
</div>


