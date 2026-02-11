<script lang="ts">

    import type {DatasetConfig} from "@lib/types";

    export let dataset_key: string;
    export let dataset: DatasetConfig;

</script>

<div class="flex p-5 w-full flex-col rounded-2xl border-2 border-[#1F1E1D20] bg-white">
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
    <div class="flex flex-row gap-2 mt-4">
        {#each Object.keys(dataset.subsets) as subset}
            <a class="bg-indigo-100 text-indigo-700 px-3 py-2 rounded-xl transition hover:bg-indigo-200" href={`/datasets/${dataset_key}/${subset}`}>
                {dataset.subsets[subset].name}
            </a>
        {/each}
    </div>
</div>

