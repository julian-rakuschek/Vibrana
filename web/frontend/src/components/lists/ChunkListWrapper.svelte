<script lang="ts">
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {type AnomalyMetric, type ChunkListSettingsType, SortMode} from "@lib/types";
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import ChunkList from "@components/lists/ChunkList.svelte";
    import {fly} from "svelte/transition"
    import {getContext} from "svelte";
    import {Jumper} from "svelte-loading-spinners";
    import {sessionGetAll} from "@lib/helper/sessionStorageHelper";

    export let dataset: string;
    export let subset: string;

    export let settings: ChunkListSettingsType;

    export let selectModeActive: boolean;


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
    const anomalyRatiosQuery = ro ?
        useQueryFetch(ApiRoutes.getAnomalyRatiosRO, {params: {dataset, subset}, data: sessionGetAll(dataset)}) :
        useQueryFetch(ApiRoutes.getAnomalyRatios, {params: {dataset, subset}})
    const normalTubeQuery = ro ?
        useQueryFetch(ApiRoutes.getNormalTubeRO, {params: {dataset, subset}, data: sessionGetAll(dataset)}) :
        useQueryFetch(ApiRoutes.getNormalTube, {params: {dataset, subset}})
    let anomaly_ratios: AnomalyMetric[] = []

    anomalyRatiosQuery.subscribe((value) => {
        if (value.isSuccess) {
            anomaly_ratios = value.data
        }
    })


</script>

{#if $chunkListQuery.isPending || $normalsQuery.isPending || $normalTubeQuery.isPending}
    <p>Loading ...</p>
{/if}

{#if $anomalyRatiosQuery.isPending || $anomalyRatiosQuery.isRefetching || $anomalyRatiosQuery.isLoading}
    <div transition:fly={{ x: -30, duration: 300 }}
         class="fixed bottom-10 left-10 text-center px-4 py-2 bg-indigo-700 text-white rounded-md flex flex-row justify-center items-center gap-3 z-50">
        <span>Fetching anomaly scores</span>
        <Jumper color="white" size="30"/>
    </div>
{/if}

{#if $chunkListQuery.isSuccess && $normalsQuery.isSuccess && $normalTubeQuery.isSuccess}
    <div class="flex flex-row flex-wrap gap-6 py-4 justify-center">
        <ChunkList
                chunks={sort_chunks($chunkListQuery.data, anomaly_ratios)} dataset={dataset} subset={subset}
                normals={$normalsQuery.data}
                anomaly_ratios={anomaly_ratios} selectModeActive={selectModeActive} normalTube={$normalTubeQuery.data}
        />
    </div>
{/if}
