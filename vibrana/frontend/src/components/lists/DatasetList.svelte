<script lang="ts">
    import {page} from '$app/state';
    import DatasetListItem from "@components/lists/DatasetListItem.svelte";

    const datasets = page.data.config
</script>

<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 w-full gap-4 p-6 justify-center items-start h-full font-[Poppins] bg-[#faf9f5]">
    {#each Object.keys(datasets) as ds}
        <DatasetListItem dataset={datasets[ds]} dataset_key={ds} />
    {/each}
</div>


