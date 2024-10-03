<script lang="ts">
    import {page} from '$app/stores';
    import ThreeChartsWrapper from "@components/charts/ThreeChartsWrapper.svelte";

    $: machine = $page.params.machine;
    $: sample = $page.params.sample;
</script>

<ThreeChartsWrapper sampleId={sample} machineId={machine} />