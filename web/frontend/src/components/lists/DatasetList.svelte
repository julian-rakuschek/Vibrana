<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";

    const datasetListQuery = useQueryFetch(ApiRoutes.getDatasetList)

</script>

<div class="w-1/2 ml-auto mr-auto">
    {#if $datasetListQuery.isLoading || $datasetListQuery.isPending}
        <CenteredLoadingSpinner/>
    {:else if $datasetListQuery.isSuccess}
        {#each $datasetListQuery.data as dataset}
            <div class="flex flex-col my-10 gap-2">
                <p class="text-xl font-semibold">{dataset.name}</p>
                <p class="text-sm text-black/80">{dataset.description}</p>
                <div class="grid grid-cols-4 gap-4">
                    {#each dataset.subsets as subset }
                        <a href={`/datasets/${dataset.folder}/${subset.folder}`} class="text-center shadow-lg p-2 cursor-default rounded-lg transition hover:-translate-y-2">{subset.name}</a>
                    {/each}
                </div>
            </div>
        {/each}
    {/if}
</div>
