<script lang="ts">
    import {page} from '$app/state';
    import DatasetListItem from "@components/lists/DatasetListItem.svelte";

    const datasets = page.data.config
</script>

<div class="w-full h-full font-[Poppins] bg-[#faf9f5]">
    <div class="flex flex-col gap-4 w-full lg:w-1/2 mx-auto">
        {#each Object.keys(datasets) as ds}
            <DatasetListItem dataset={datasets[ds]} dataset_key={ds}/>
        {/each}
    </div>
</div>


