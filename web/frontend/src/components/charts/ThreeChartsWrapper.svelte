<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import ThreeCharts from "@components/charts/ThreeCharts.svelte";
    import {Icon, ArrowLeft} from "svelte-hero-icons";
    import {getContext} from "svelte";
    import {sessionGetAll, setItemSeen} from "@lib/helper/sessionStorageHelper";
    import {Jumper} from "svelte-loading-spinners";
    import {fly} from "svelte/transition"

    export let dataset: string;
    export let subset: string;
    export let chunk: string;

    setItemSeen(dataset, subset, chunk)

    const {ro} = getContext("ro") as { ro: boolean }

    const timeSeriesQuery = useQueryFetch(ApiRoutes.getChunkValues, {params: {dataset, subset, chunk}})
    const projectedValuesQuery = useQueryFetch(ApiRoutes.getChunkProjected, {params: {dataset, subset, chunk}})
    const normalTubeQuery = ro ?
        useQueryFetch(ApiRoutes.getNormalTubeRO, {params: {dataset, subset}, data: sessionGetAll(dataset, subset)}) :
        useQueryFetch(ApiRoutes.getNormalTube, {params: {dataset, subset}})
    const similaritiesQuery = ro ?
        useQueryFetch(ApiRoutes.getSimilaritiesRO, {params: {dataset, subset, chunk}, data: sessionGetAll(dataset, subset)}) :
        useQueryFetch(ApiRoutes.getSimilarities, {params: {dataset, subset, chunk}})
    const mdsEmbeddingQuery = useQueryFetch(ApiRoutes.getMDSEmbedding, {params: {dataset, subset, chunk}})
    const labelsQuery = useQueryFetch(ApiRoutes.getLabels, {params: {dataset, subset, chunk}}, undefined, undefined, ro)
    const eventsQuery = useQueryFetch(ApiRoutes.getChunkEvents, {params: {dataset, subset, chunk}})
    const freqQuery = useQueryFetch(ApiRoutes.getChunkFreq, {params: {dataset, subset, chunk}})
</script>

<a class="fixed top-3 left-3 bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl z-10" href={`/datasets/${dataset}/${subset}`}>
    <Icon src="{ArrowLeft}" class="w-5 h-5" />
</a>
{#if $normalTubeQuery.isPending || $similaritiesQuery.isRefetching || $mdsEmbeddingQuery.isLoading || $freqQuery.isLoading}
    <div transition:fly={{ x: -30, duration: 300 }}
         class="fixed bottom-10 left-10 text-center px-4 py-2 bg-indigo-700 text-white rounded-md flex flex-row justify-center items-center gap-3 z-50">
        <div>
            {#if $normalTubeQuery.isPending}
                <p>Fetching normal tube</p>
            {/if}
            {#if $similaritiesQuery.isPending}
                <p>Fetching similarities</p>
            {/if}
            {#if $mdsEmbeddingQuery.isPending}
                <p>Fetching MDS embedding</p>
            {/if}
            {#if $freqQuery.isPending}
                <p>Fetching frequency coloring</p>
            {/if}
        </div>
        <Jumper color="white" size="30"/>
    </div>
{/if}
{#if $timeSeriesQuery.isPending || $projectedValuesQuery.isPending || $labelsQuery.isPending || $eventsQuery.isPending}
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
            normalTube={$normalTubeQuery.isSuccess ? $normalTubeQuery.data : [0, 0]}
            similarities={$similaritiesQuery.isSuccess ? $similaritiesQuery.data : []}
            mdsEmbedding={$mdsEmbeddingQuery.isSuccess ? $mdsEmbeddingQuery.data : []}
            labels={$labelsQuery.data}
            events={$eventsQuery.data}
            freq={$freqQuery.isSuccess ? $freqQuery.data : []}
    />
{/if}