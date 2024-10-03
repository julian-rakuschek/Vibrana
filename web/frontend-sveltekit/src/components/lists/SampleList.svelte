<script lang="ts">
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {type SamplesSettingsType, SortMode} from "@lib/types";
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {useQueryClient} from "@tanstack/svelte-query";
    import {goto} from "$app/navigation";
    import SampleCard from "@components/SampleCard.svelte";

    export let machine: string;

    export let settings: SamplesSettingsType;

    export let selectModeActive: boolean;

    const sort_samples = (samples: string[], anomaly_ratios: [string, number][]) => {
        let sample_sorted = samples.sort();
        if (settings.sort === SortMode.Score && anomaly_ratios && samples) {
            sample_sorted = anomaly_ratios.map(s => s[0])
        }
        return sample_sorted
    }


    const client = useQueryClient()
    const sampleListQuery = useQueryFetch(ApiRoutes.getMachineSamples, {params: {machine}})
    const normalsQuery = useQueryFetch(ApiRoutes.getNormals, {params: {machineId: machine}})
    const anomalyRatiosQuery = useQueryFetch(ApiRoutes.getAnomalyRatios, {params: {machineId: machine}})

    const handleClick = async (sampleId: string) => {
        if (selectModeActive && $normalsQuery.data) {
            if ($normalsQuery.data.indexOf(sampleId) === -1) {
                await ApiRoutes.addNormal.fetch({params: {machineId: machine, sampleId: sampleId}})
            }
            else {
                await ApiRoutes.removeNormal.fetch({params: {machineId: machine, sampleId: sampleId}})
            }
            await client.invalidateQueries();
        }
        else goto(`/machines/${machine}/analyze/${sampleId}`)
    }

</script>

{#if $sampleListQuery.isPending || $normalsQuery.isPending || $anomalyRatiosQuery.isPending}
    <p>Loading ...</p>
{/if}

{#if $sampleListQuery.isSuccess && $normalsQuery.isSuccess && $anomalyRatiosQuery.isSuccess}
    <div class="flex flex-row flex-wrap gap-6 py-4 justify-center">
        {#if !settings.split}
            {#each sort_samples($sampleListQuery.data, $anomalyRatiosQuery.data) as sample}
                <div class="flex flex-row flex-wrap gap-6 py-4 justify-center" on:click={() => handleClick(sample)}>
                    <SampleCard
                            sampleId={sample} machineId={machine} selected={$normalsQuery.data.indexOf(sample) !== -1}
                            selectModeActive={selectModeActive} anomalyRatio={$anomalyRatiosQuery.data.find(value => value[0] == sample)[1]} />
                </div>
            {/each}
        {:else}
            <div class="flex flex-row gap-20">
                <div class="flex flex-col gap-4">
                    {#each sort_samples($sampleListQuery.data, $anomalyRatiosQuery.data).filter(s => s.startsWith("normal")) as sample}
                        <div class="flex flex-row flex-wrap gap-6 py-4 justify-center" on:click={() => handleClick(sample)}>
                            <SampleCard sampleId={sample} machineId={machine} selected={$normalsQuery.data.indexOf(sample) !== -1} selectModeActive={selectModeActive} anomalyRatio={$anomalyRatiosQuery.data.find(value => value[0] == sample)[1]} />
                        </div>
                    {/each}
                </div>
                <div class="flex flex-col gap-4">
                    {#each sort_samples($sampleListQuery.data, $anomalyRatiosQuery.data).filter(s => s.startsWith("abnormal")) as sample}
                        <div class="flex flex-row flex-wrap gap-6 py-4 justify-center" on:click={() => handleClick(sample)}>
                            <SampleCard sampleId={sample} machineId={machine} selected={$normalsQuery.data.indexOf(sample) !== -1} selectModeActive={selectModeActive} anomalyRatio={$anomalyRatiosQuery.data.find(value => value[0] == sample)[1]} />
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
{/if}
