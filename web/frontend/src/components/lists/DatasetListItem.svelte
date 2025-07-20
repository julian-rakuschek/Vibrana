<script lang="ts">

    import type {DatasetConfig} from "@lib/types";

    export let dataset_key: string;
    export let dataset: DatasetConfig;

</script>

<div>
    <p class="font-bold underline mt-4">{dataset.name}</p>
    <p class="text-sm my-1">{dataset.source}</p>
    <p class="text-sm italic">{dataset.description}</p>
    <ul class="list-inside list-disc mt-2">
        {#each Object.keys(dataset.subsets) as subset}
            <li><a class="text-indigo-500 hover:text-indigo-700" href={`/datasets/${dataset_key}/${subset}/pda`}>{dataset.subsets[subset].name}</a></li>
        {/each}
    </ul>
</div>

