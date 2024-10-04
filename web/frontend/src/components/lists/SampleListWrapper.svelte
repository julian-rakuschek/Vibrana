<script lang="ts">
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {type AnomalyMetric, type SamplesSettingsType, SortMode} from "@lib/types";
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import SampleList from "@components/lists/SampleList.svelte";
    import { fly } from "svelte/transition"
    import {onMount} from "svelte";
    import {Jumper} from "svelte-loading-spinners";

    export let machineId: string;

    export let settings: SamplesSettingsType;

    export let selectModeActive: boolean;

    const sort_samples = (samples: string[], anomaly_ratios: AnomalyMetric[]): string[] => {
        let sample_sorted = samples.sort();
        if (settings.sort === SortMode.Score && anomaly_ratios.length == samples.length && samples) {
            sample_sorted = anomaly_ratios.map(s => s.sampleId)
        }
        return sample_sorted
    }


    const sampleListQuery = useQueryFetch(ApiRoutes.getMachineSamples, {params: {machineId}})
    const normalsQuery = useQueryFetch(ApiRoutes.getNormals, {params: {machineId}})
    const anomalyRatiosQuery = useQueryFetch(ApiRoutes.getAnomalyRatios, {params: {machineId}})
    let anomaly_ratios: AnomalyMetric[] = []
    let fetching_anomalies = false;

    anomalyRatiosQuery.subscribe((value) => {
        if (value.isSuccess) {
            anomaly_ratios = value.data
            fetching_anomalies = false;
        }
    })

    onMount(() => {
        fetching_anomalies = anomaly_ratios.length == 0
    })

</script>

{#if $sampleListQuery.isPending || $normalsQuery.isPending}
    <p>Loading ...</p>
{/if}

{#if fetching_anomalies}
    <div transition:fly={{ x: -30, duration: 300 }} class="fixed bottom-10 left-10 text-center px-4 py-2 bg-indigo-700 text-white rounded-md flex flex-row justify-center items-center gap-3 z-50">
        <span>Fetching anomaly scores</span> <Jumper color="white" size="30" />
    </div>
{/if}

{#if $sampleListQuery.isSuccess && $normalsQuery.isSuccess}
    <div class="flex flex-row flex-wrap gap-6 py-4 justify-center">
        {#if !settings.split}
            <SampleList samples={sort_samples($sampleListQuery.data, anomaly_ratios)} machineId={machineId} normals={$normalsQuery.data}
                        anomaly_ratios={anomaly_ratios} selectModeActive={selectModeActive} bind:fetching_anomalies/>
        {:else}
            <div class="flex flex-row gap-20">
                <div class="flex flex-col gap-4">
                    <SampleList samples={sort_samples($sampleListQuery.data, anomaly_ratios).filter(s => s.startsWith("normal"))}
                                machineId={machineId} normals={$normalsQuery.data} anomaly_ratios={anomaly_ratios}
                                selectModeActive={selectModeActive} bind:fetching_anomalies/>
                </div>
                <div class="flex flex-col gap-4">
                    <SampleList samples={sort_samples($sampleListQuery.data, anomaly_ratios).filter(s => s.startsWith("abnormal"))}
                                machineId={machineId} normals={$normalsQuery.data} anomaly_ratios={anomaly_ratios}
                                selectModeActive={selectModeActive} bind:fetching_anomalies/>
                </div>
            </div>
        {/if}
    </div>
{/if}
