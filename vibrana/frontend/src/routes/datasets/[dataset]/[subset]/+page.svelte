<script lang="ts">
    import Navbar from '@components/navigation/Navbar.svelte';
    import {page} from '$app/state';
    import ClusterAnalysis
        from "@components/clusterAnalysis/ClusterAnalysis.svelte";

    $: dataset = page.params.dataset;
    $: subset = page.params.subset;
</script>

<Navbar/>
<ClusterAnalysis dataset={dataset} subset={subset}/>