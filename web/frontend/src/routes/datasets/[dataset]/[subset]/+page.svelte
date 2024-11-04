<script lang="ts">
    import {page} from '$app/stores';
    import Navbar from "@components/Navbar.svelte";
    import {type ChunkListSettingsType, type Dataset, SortMode} from "@lib/types";
    import SampleListSettings from "@components/ChunkListSettings.svelte";
    import ChunkListWrapper from "@components/lists/ChunkListWrapper.svelte";
    import {ArrowLeft, Icon, ArrowsUpDown, ArrowsRightLeft} from "svelte-hero-icons";
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {displayMode} from "@lib/stores"

    let settings: ChunkListSettingsType = {sort: SortMode.Name, split: false}

    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;

    const datasetListQuery = useQueryFetch(ApiRoutes.getDatasetList)

    const get_subset_name = (data: Dataset[]): string => {
        for (const ds of data) {
            for (const ss of ds.subsets) {
                if (ss.folder === subset && ds.folder === dataset) return ss.name
            }
        }
        return subset
    }
</script>

<Navbar/>
<div class="h-full col-span-full px-10 ">
    <div class="w-full grid grid-cols-3 justify-between relative z-20 h-10">
        <div class="flex flex-row gap-3 items-center place-self-start">
            <a class="bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10" href={`/datasets`}>
                <Icon src="{ArrowLeft}" class="w-5 h-5"/>
            </a>
            <span class="text-xl font-semibold">
                {#if $datasetListQuery.data && $datasetListQuery.isSuccess}
                    {get_subset_name($datasetListQuery.data)}
                {/if}
            </span>
        </div>
        <div class="flex flex-row w-full justify-center gap-3 place-self-start">
            <button class={`${$displayMode === "vertical" ? "bg-indigo-600 text-white" : "bg-white text-black"} rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10`} on:click={() => displayMode.set("vertical")}>
                <Icon src="{ArrowsUpDown}" class="w-5 h-5"/>
            </button>
            <button class={`${$displayMode === "horizontal" ? "bg-indigo-600 text-white" : "bg-white text-black"} rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10`}
                    on:click={() => displayMode.set("horizontal")}>
                <Icon src="{ArrowsRightLeft}" class="w-5 h-5"/>
            </button>
        </div>
        <div class="place-self-end h-full">
            <SampleListSettings bind:settings dataset={dataset} subset={subset}/>
        </div>
    </div>
    <ChunkListWrapper dataset={dataset} subset={subset} settings={settings} displayMode={$displayMode}/>
</div>
