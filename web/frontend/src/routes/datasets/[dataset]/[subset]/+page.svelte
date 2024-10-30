<script lang="ts">
    import {page} from '$app/stores';
    import Navbar from "@components/Navbar.svelte";
    import SampleList from "@components/lists/SampleListWrapper.svelte";
    import {type ChunkListSettingsType, SortMode} from "@lib/types";
    import SampleListSettings from "@components/SampleListSettings.svelte";
    import UploadPopup from "@components/UploadPopup.svelte";
    import {getContext} from "svelte";
    import ChunkListWrapper from "@components/lists/ChunkListWrapper.svelte";

    let settings: ChunkListSettingsType = {sort: SortMode.Name, split: false}
    let selectModeActive: boolean = false
    let uploadOpen = false;

    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;

    const {ro} = getContext("ro") as { ro: boolean }
</script>

<Navbar />
<ChunkListWrapper dataset={dataset} subset={subset} settings={settings} selectModeActive={selectModeActive}  />