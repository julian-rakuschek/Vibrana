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
            <span class="text-xl font-semibold">Chunks</span>
        </div>
        <div class="absolute top-0 right-0">
            <SampleListSettings bind:settings dataset={dataset} subset={subset}/>
        </div>
    </div>
    <ChunkListWrapper dataset={dataset} subset={subset} settings={settings} selectModeActive={selectModeActive}/>
</div>
