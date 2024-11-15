<script lang="ts">
    import {page} from '$app/stores';
    import Navbar from "@components/manage/Navbar.svelte";
    import {type ChunkListSettingsType, type Dataset, SortMode} from "@lib/types";
    import SampleListSettings from "@components/lists/ChunkListSettings.svelte";
    import ChunkListWrapper from "@components/lists/ChunkListWrapper.svelte";
    import {ArrowLeft, Icon} from "svelte-hero-icons";
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {displayMode} from "@lib/stores"
    import TableIcon from "@components/icons/TableIcon.svelte";
    import GridIcon from "@components/icons/GridIcon.svelte";
    import ClusterIcon from "@components/icons/ClusterIcon.svelte";

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
<div class="grow px-10 flex flex-col overflow-y-scroll pb-10">
    <div class="w-full grid grid-cols-3 relative z-20 h-10">
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
        <div class="flex flex-row w-full justify-center pt-2 gap-3 place-self-start">
            <button class={`${$displayMode === "table" ? "bg-indigo-600 text-white" : "bg-white text-black"} gap-2 rounded-full shadow-lg px-4 py-2 flex justify-center items-center transition hover:shadow-xl z-10`}
                    on:click={() => displayMode.set("table")}>
                <TableIcon class="w-5 h-5" fill={$displayMode === "table" ? "white" : "black"}/>
                Table
            </button>
            <button class={`${$displayMode === "grid" ? "bg-indigo-600 text-white" : "bg-white text-black"} gap-2 rounded-full shadow-lg px-4 py-2 flex justify-center items-center transition hover:shadow-xl z-10`}
                    on:click={() => displayMode.set("grid")}>
                <GridIcon class="w-5 h-5" fill={$displayMode === "grid" ? "white" : "black"}/>
                Grid
            </button>
            <button class={`${$displayMode === "cluster" ? "bg-indigo-600 text-white" : "bg-white text-black"} gap-2 rounded-full shadow-lg px-4 py-2 flex justify-center items-center transition hover:shadow-xl z-10`}
                    on:click={() => displayMode.set("cluster")}>
                <ClusterIcon class="w-5 h-5" fill={$displayMode === "cluster" ? "white" : "black"}/>
                Cluster
            </button>
        </div>
        <div class="place-self-end h-full">
            <SampleListSettings bind:settings dataset={dataset} subset={subset}/>
        </div>
    </div>
    <div class="grow overflow-y-scroll pt-5">
        <ChunkListWrapper dataset={dataset} subset={subset} settings={settings} displayMode={$displayMode}/>
    </div>
</div>
