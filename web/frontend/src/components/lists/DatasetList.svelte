<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import StyledDisclosure from "@components/atoms/StyledDisclosure.svelte";
    import {Icon, Link} from "svelte-hero-icons";

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
                            <a href={`/datasets/${dataset.folder}/${subset.folder}`}
                               class="text-center p-2 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-200">{subset.name}</a>
                        {/each}
                    </div>
                    <div class="flex flex-row w-full gap-4">
                        <div class="bg-teal-50 text-teal-600 grow rounded-lg px-2 py-1">
                            <span class="font-semibold">Task:</span> {dataset.task}
                        </div>
                        {#if dataset.source.startsWith("http")}
                            <a class="bg-teal-50 text-teal-600 rounded-lg px-2 py-1 flex flex-row flex-nowrap gap-2 items-center hover:bg-teal-100" href="{dataset.source}" target="_blank">
                                <Icon src="{Link}" class="h-4 w-4"></Icon>
                                <span class="font-semibold">Source</span>
                            </a>
                        {:else}
                            <div class="bg-teal-50 text-teal-600 rounded-lg px-2 py-1">{dataset.source}</div>
                        {/if}
                    </div>
                </StyledDisclosure>
            {/each}
        </div>
    {/if}
</div>
