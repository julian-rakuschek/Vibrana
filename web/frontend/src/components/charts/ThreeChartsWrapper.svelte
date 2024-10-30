<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import ThreeCharts from "@components/charts/ThreeCharts.svelte";
    import {Icon, ArrowLeft} from "svelte-hero-icons";
    import {getContext} from "svelte";
    import {sessionGetAll, setItemSeen} from "@lib/helper/sessionStorageHelper";

    export let dataset: string;
    export let subset: string;
    export let chunk: string;

    setItemSeen(dataset, chunk)

    const {ro} = getContext("ro") as { ro: boolean }

    const timeSeriesQuery = useQueryFetch(ApiRoutes.getChunkValues, {params: {dataset, subset, chunk}})
    const projectedValuesQuery = useQueryFetch(ApiRoutes.getChunkProjected, {params: {dataset, subset, chunk}})
    const normalTubeQuery = ro ?
        useQueryFetch(ApiRoutes.getNormalTubeRO, {params: {dataset, subset}, data: sessionGetAll(dataset)}) :
        useQueryFetch(ApiRoutes.getNormalTube, {params: {dataset, subset}})
    const similaritiesQuery = ro ?
        useQueryFetch(ApiRoutes.getSimilaritiesRO, {params: {dataset, subset, chunk}, data: sessionGetAll(dataset)}) :
        useQueryFetch(ApiRoutes.getSimilarities, {params: {dataset, subset, chunk}})
    const mdsEmbeddingQuery = useQueryFetch(ApiRoutes.getMDSEmbedding, {params: {dataset, subset, chunk}})
    const labelsQuery = useQueryFetch(ApiRoutes.getLabels, {params: {dataset, subset, chunk}}, undefined, undefined, ro)
    const eventsQuery = useQueryFetch(ApiRoutes.getChunkEvents, {params: {dataset, subset, chunk}})
    const freqQuery = useQueryFetch(ApiRoutes.getChunkFreq, {params: {dataset, subset, chunk}})
</script>

<a class="fixed top-3 left-3 bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10" href={`/datasets/${dataset}/${subset}`}>
    <Icon src="{ArrowLeft}" class="w-5 h-5" />
</a>
{#if $timeSeriesQuery.isPending || $projectedValuesQuery.isPending || $normalTubeQuery.isPending || $similaritiesQuery.isPending || $mdsEmbeddingQuery.isPending || $labelsQuery.isPending || $eventsQuery.isPending || $freqQuery.isPending}
    <div class="absolute top-0 right-0 w-full h-full">
        <CenteredLoadingSpinner/>
    </div>
{:else}
    <ThreeCharts
            dataset={dataset}
            subset={subset}
            chunk={chunk}
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