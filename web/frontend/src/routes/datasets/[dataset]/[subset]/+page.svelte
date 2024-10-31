<script lang="ts">
    import {page} from '$app/stores';
    import Navbar from "@components/Navbar.svelte";
    import {type ChunkListSettingsType, SortMode} from "@lib/types";
    import SampleListSettings from "@components/ChunkListSettings.svelte";
    import ChunkListWrapper from "@components/lists/ChunkListWrapper.svelte";
    import {ArrowLeft, Icon, ArrowsUpDown, ArrowsRightLeft} from "svelte-hero-icons";

    let settings: ChunkListSettingsType = {sort: SortMode.Name, split: false}
    let displayMode: string = "vertical"


    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;
</script>

<Navbar/>
<div class="h-full col-span-full px-10 ">
    <div class="w-full flex flex-row flex-nowrap justify-between relative z-20 h-10">
        <div class="flex flex-row gap-3 items-center">
            <a class="bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10" href={`/datasets`}>
                <Icon src="{ArrowLeft}" class="w-5 h-5"/>
            </a>
            <span class="text-xl font-semibold">Chunks</span>
        </div>
        <div class="flex flex-row gap-3">
           <button class={`${displayMode === "vertical" ? "bg-indigo-600 text-white" : "bg-white text-black"} rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10`} on:click={() => displayMode = "vertical"}>
                <Icon src="{ArrowsUpDown}" class="w-5 h-5"/>
            </button>
            <button class={`${displayMode === "horizontal" ? "bg-indigo-600 text-white" : "bg-white text-black"} rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10`} on:click={() => displayMode = "horizontal"} >
                <Icon src="{ArrowsRightLeft}" class="w-5 h-5"/>
            </button>
        </div>
        <div>
            <SampleListSettings bind:settings dataset={dataset} subset={subset}/>
        </div>
    </div>
    <ChunkListWrapper dataset={dataset} subset={subset} settings={settings} displayMode={displayMode} />
</div>
