<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import ThreeCharts from "@components/charts/ThreeCharts.svelte";
    import {Icon, ArrowLeft} from "svelte-hero-icons";

    export let machineId: string;
    export let sampleId: string;

    const timeSeriesQuery = useQueryFetch(ApiRoutes.getSampleValues, {params: {machineId, sampleId}})
    const projectedValuesQuery = useQueryFetch(ApiRoutes.getSampleProjected, {params: {machineId, sampleId}})
    const normalTubeQuery = useQueryFetch(ApiRoutes.getNormalTube, {params: {machineId}})
    const similaritiesQuery = useQueryFetch(ApiRoutes.getSimilarities, {params: {machineId, sampleId}})
    const mdsEmbeddingQuery = useQueryFetch(ApiRoutes.getMDSEmbedding, {params: {machineId, sampleId}})
    const labelsQuery = useQueryFetch(ApiRoutes.getLabels, {params: {machineId, sampleId}})
    const eventsQuery = useQueryFetch(ApiRoutes.getSampleEvents, {params: {machineId, sampleId}})
    const freqQuery = useQueryFetch(ApiRoutes.getSampleFreq, {params: {machineId, sampleId}})
</script>

<a class="fixed top-3 left-3 bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10" href={`/machines/${machineId}/analyze`}>
    <Icon src="{ArrowLeft}" class="w-5 h-5" />
</a>
{#if $timeSeriesQuery.isPending || $projectedValuesQuery.isPending || $normalTubeQuery.isPending || $similaritiesQuery.isPending || $mdsEmbeddingQuery.isPending || $labelsQuery.isPending || $eventsQuery.isPending || $freqQuery.isPending}
    <div class="absolute top-0 right-0 w-full h-full">
        <CenteredLoadingSpinner/>
    </div>
{:else}
    <ThreeCharts
            machineId={machineId}
            sampleId={sampleId}
            timeSeries={$timeSeriesQuery.data}
            projected={$projectedValuesQuery.data}
            normalTube={$normalTubeQuery.data}
            similarities={$similaritiesQuery.data}
            mdsEmbedding={$mdsEmbeddingQuery.data}
            labels={$labelsQuery.data}
            events={$eventsQuery.data}
            freq={$freqQuery.data}
    />
{/if}