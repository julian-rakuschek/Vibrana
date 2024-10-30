<script lang="ts">
    import {page} from '$app/stores';
    import Navbar from "@components/Navbar.svelte";
    import {type ChunkListSettingsType, SortMode} from "@lib/types";
    import SampleListSettings from "@components/ChunkListSettings.svelte";
    import ChunkListWrapper from "@components/lists/ChunkListWrapper.svelte";

    let settings: ChunkListSettingsType = {sort: SortMode.Name, split: false}
    let selectModeActive: boolean = false

    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;
</script>

<Navbar/>
<div class="h-full col-span-full px-10 ">
    <div class="w-full flex flex-row flex-nowrap justify-between relative z-20 h-10">
        <div>
            <span class="text-xl font-semibold">Samples</span>
        </div>

        <button on:click={() => selectModeActive = !selectModeActive}
                class={`${selectModeActive ? "bg-green-600 text-white" : "bg-white text-green-600"}  border-green-600 border-2 border-solid rounded-lg px-3 py-1 mr-20 flex flex-row flex-nowrap items-center gap-2 cursor-default transition`}>
            {!selectModeActive ? "Select Anomaly-Free Samples" : "Exit Selection Mode"}
        </button>
        <div class="absolute top-0 right-0">
            <SampleListSettings bind:settings dataset={dataset} subset={subset}/>
        </div>
    </div>
    <ChunkListWrapper dataset={dataset} subset={subset} settings={settings} selectModeActive={selectModeActive}/>
</div>
