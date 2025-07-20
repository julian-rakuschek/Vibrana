<script lang="ts">
    import PDA from '@components/pda/PDA.svelte';
    import Navbar from '@components/manage/Navbar.svelte';
    import {page} from '$app/stores';

    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;
</script>

<Navbar/>
<PDA dataset={dataset} subset={subset}/>