<script lang="ts">
    import Navbar from '@components/manage/Navbar.svelte';
    import {page} from '$app/stores';
    import LargeSignalAnalysisWrapper
        from "@components/dataset-analysis/large-signal-pda/LargeSignalAnalysisWrapper.svelte";

    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;
</script>

<Navbar/>
<LargeSignalAnalysisWrapper dataset={dataset} subset={subset}/>