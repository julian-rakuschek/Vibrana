<script lang="ts">
    import {page} from '$app/stores';
    import ThreeChartsWrapper from "@components/charts/ThreeChartsWrapper.svelte";

    $: dataset = $page.params.dataset;
    $: subset = $page.params.subset;
    $: chunk = $page.params.chunk;
</script>

<ThreeChartsWrapper dataset="{dataset}" subset="{subset}" chunk="{chunk}" />