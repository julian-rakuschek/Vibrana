<script lang="ts">
    import {page} from '$app/stores';
    import Navbar from "@components/Navbar.svelte";
    import SampleList from "@components/lists/SampleListWrapper.svelte";
    import {type SamplesSettingsType, SortMode} from "@lib/types";
    import SampleListSettings from "@components/SampleListSettings.svelte";
    import UploadPopup from "@components/UploadPopup.svelte";
    import {getContext} from "svelte";

    let settings: SamplesSettingsType = {sort: SortMode.Score, split: false}
    let selectModeActive: boolean = false
    let uploadOpen = false;

    $: machine = $page.params.machine;

    const {ro} = getContext("ro") as { ro: boolean }
</script>

<Navbar/>
<div class="grow grid grid-cols-12">
    <div class="h-full col-span-full px-10 ">
        <div class="w-full flex flex-row flex-nowrap justify-between relative z-20 h-10">
            <div>
                <span class="text-xl font-semibold">Samples</span>
                {#if !ro}
                    <button on:click={() => uploadOpen = true} class="rounded-md bg-indigo-50 px-2.5 py-1.5 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-100">Upload</button>
                {/if}
            </div>

            <button on:click={() => selectModeActive = !selectModeActive}
                    class={`${selectModeActive ? "bg-green-600 text-white" : "bg-white text-green-600"}  border-green-600 border-2 border-solid rounded-lg px-3 py-1 mr-20 flex flex-row flex-nowrap items-center gap-2 cursor-default transition`}>
                {!selectModeActive ? "Select Anomaly-Free Samples" : "Exit Selection Mode"}
            </button>
            <div class="absolute top-0 right-0">
                <SampleListSettings bind:settings machine={machine}/>
            </div>
        </div>
        <SampleList machineId={machine} settings={settings} selectModeActive={selectModeActive}/>
    </div>
    <div class="h-full col-span-4 hidden">
        <div class="w-full flex flex-row flex-nowrap justify-between px-5">
            <span class="text-xl font-semibold">Live</span>
        </div>
    </div>
</div>

<UploadPopup bind:isOpen={uploadOpen} machine={machine}/>