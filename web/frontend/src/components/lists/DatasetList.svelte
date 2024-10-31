<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import StyledDisclosure from "@components/atoms/StyledDisclosure.svelte";

    const datasetListQuery = useQueryFetch(ApiRoutes.getDatasetList)

</script>

<div class="w-1/2 ml-auto mr-auto">
    <p class="text-xl font-semibold mb-5">Datasets</p>
    {#if $datasetListQuery.isLoading || $datasetListQuery.isPending}
        <CenteredLoadingSpinner/>
    {:else if $datasetListQuery.isSuccess}
        <div class="flex flex-col gap-2">
            {#each $datasetListQuery.data as dataset}
                <StyledDisclosure header_text="{dataset.name}">
                    <p class="text-sm text-black/80">{dataset.description}</p>
                    <div class="flex flex-col gap-3">
                        {#each dataset.subsets as subset }
                            <a href={`/datasets/${dataset.folder}/${subset.folder}`} class="text-center p-2 rounded-lg bg-indigo-50 text-indigo-600 transition hover:bg-indigo-200">{subset.name}</a>
                        {/each}
                    </div>
                </StyledDisclosure>
            {/each}
        </div>
    {/if}
</div>
