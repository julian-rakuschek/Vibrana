<script lang="ts">

    import type {DatasetConfig} from "@lib/types";

    export let dataset_key: string;
    export let dataset: DatasetConfig;

</script>

<div class="w-full md:w-2/3 lg:w-1/2 flex px-10 py-3 flex-col rounded-2xl border-2 border-[#1F1E1D20] bg-white h-full">
    <div><span class="text-xs bg-[#997652] text-white px-2 rounded-full">{dataset.dataset_type}</span></div>
    <p class="font-bold underline">{dataset.name}</p>
    {#if dataset.source}
        {#if dataset.source.startsWith("http")}
            <a class="text-sm italic text-indigo-500 hover:text-indigo-700"
               href={dataset.source}>{dataset.source.replace("https://", "")}</a>
        {:else}
            <p class="text-sm italic">{dataset.source}</p>
        {/if}
    {/if}
    {#if dataset.description}<p class="text-sm italic">{dataset.description}</p>{/if}
    {#if dataset.dataset_type === "stream"}
        <ul class="list-inside list-disc mt-2">
            {#each Object.keys(dataset.subsets) as subset}
                <li><a class="text-indigo-500 hover:text-indigo-700"
                       href={`/datasets/${dataset_key}/${subset}/pda`}>{dataset.subsets[subset].name}</a></li>
            {/each}
        </ul>
    {:else}
        <p>Chunks are WIP</p>
    {/if}
</div>

