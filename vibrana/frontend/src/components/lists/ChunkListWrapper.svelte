<script lang="ts">
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {type AnomalyMetric, type ChunkListSettingsType, SortMode} from "@lib/types";
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import ChunkList from "@components/lists/ChunkList.svelte";
    import {fly} from "svelte/transition"
    import {getContext} from "svelte";
    import {Jumper} from "svelte-loading-spinners";
    import {sessionGetAll} from "@lib/helper/sessionStorageHelper";
    import ChunkMatrix from "@components/lists/ChunkMatrix.svelte";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import ChunkCluster from "@components/lists/ChunkCluster.svelte";

    export let dataset: string;
    export let subset: string;

    export let settings: ChunkListSettingsType;
    export let displayMode: string = "vertical"


    const sort_chunks = (chunks: string[], anomaly_ratios: AnomalyMetric[]): string[] => {
        let chunk_sorted = chunks.sort();
        if (settings.sort === SortMode.Score && anomaly_ratios.length == chunks.length && chunks) {
            chunk_sorted = anomaly_ratios.map(s => s.chunk)
        }
        return chunk_sorted
    }

    const {ro} = getContext("ro") as { ro: boolean }
    const chunkListQuery = useQueryFetch(ApiRoutes.getChunks, {params: {dataset, subset}})
    const normalsQuery = useQueryFetch(ApiRoutes.getNormals, {params: {dataset, subset}}, undefined, undefined, ro)
    const labelCountQuery = useQueryFetch(ApiRoutes.getLabelCounts, {
        params: {
            dataset,
            subset
        }
    }, undefined, undefined, ro)
    const clusteringQuery = useQueryFetch(ApiRoutes.getCluster, {params: {dataset, subset}}, undefined, undefined, ro)
    const anomalyRatiosQuery = ro ?
        useQueryFetch(ApiRoutes.getAnomalyRatiosRO, {params: {dataset, subset}, data: sessionGetAll(dataset, subset)}) :
        useQueryFetch(ApiRoutes.getAnomalyRatios, {params: {dataset, subset}})
    const normalTubeQuery = ro ?
        useQueryFetch(ApiRoutes.getNormalTubeRO, {params: {dataset, subset}, data: sessionGetAll(dataset, subset)}) :
        useQueryFetch(ApiRoutes.getNormalTube, {params: {dataset, subset}})
    let anomaly_ratios: AnomalyMetric[] = []

    anomalyRatiosQuery.subscribe((value) => {
        if (value.isSuccess) {
            anomaly_ratios = value.data
        }
    })


</script>

{#if $chunkListQuery.isPending || $normalsQuery.isPending || $normalTubeQuery.isPending || $labelCountQuery.isPending || $clusteringQuery.isPending}
    <div class="w-full h-full pt-20">
        <CenteredLoadingSpinner/>
    </div>
{/if}

{#if $anomalyRatiosQuery.isPending || $anomalyRatiosQuery.isRefetching || $anomalyRatiosQuery.isLoading || $clusteringQuery.isLoading}
    <div transition:fly={{ x: -30, duration: 300 }}
         class="fixed bottom-10 left-10 text-center px-4 py-2 bg-indigo-700 text-white rounded-md flex flex-row justify-center items-center gap-3 z-50">
        <span>Fetching anomaly scores</span>
        <Jumper color="white" size="30"/>
    </div>
{/if}

{#if $chunkListQuery.isSuccess && $normalsQuery.isSuccess && $normalTubeQuery.isSuccess && $labelCountQuery.isSuccess && $clusteringQuery.isSuccess}
    {#if displayMode === "table"}
        <ChunkList
                chunks={sort_chunks($chunkListQuery.data, anomaly_ratios)} dataset={dataset} subset={subset}
                normals={$normalsQuery.data} labelCounts={$labelCountQuery.data}
                anomaly_ratios={anomaly_ratios} normalTube={$normalTubeQuery.data}
        />
    {:else if displayMode === "grid"}
        <ChunkMatrix
                chunks={sort_chunks($chunkListQuery.data, anomaly_ratios)}
                normals={$normalsQuery.data} dataset={dataset} subset={subset}
                anomaly_ratios={anomaly_ratios} normalTube={$normalTubeQuery.data}
                labelCounts={$labelCountQuery.data}
        />
    {:else if displayMode === "cluster"}
        <ChunkCluster
                clustering={$clusteringQuery.data} normals={$normalsQuery.data}
                dataset={dataset} subset={subset}
                anomaly_ratios={anomaly_ratios} normalTube={$normalTubeQuery.data}
                labelCounts={$labelCountQuery.data}/>
    {/if}

{/if}
