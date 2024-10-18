<script lang="ts">
    import SampleCard from "@components/SampleCard.svelte";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {goto} from "$app/navigation";
    import {useQueryClient} from "@tanstack/svelte-query";
    import type {AnomalyMetric} from "@lib/types";
    import {getContext} from "svelte";
    import {sessionToggleNormal} from "@lib/helper/sessionStorageHelper";

    export let samples: string[];
    export let machineId: string;
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let selectModeActive: boolean;
    export let normalTube: [number, number];

    const client = useQueryClient()

    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.sampleId == needle)
        if (res) return res;
        else return undefined;
    }

    const {ro} = getContext("ro") as { ro: boolean }

    const handleClick = async (sampleId: string) => {
        if (selectModeActive && normals) {
            if (ro) sessionToggleNormal(machineId, sampleId)
            else{
                if (normals.indexOf(sampleId) === -1) {
                    await ApiRoutes.addNormal.fetch({params: {machineId, sampleId}})
                } else {
                    await ApiRoutes.removeNormal.fetch({params: {machineId, sampleId}})
                }
            }
            await client.invalidateQueries();
        }
        else goto(`/machines/${machineId}/analyze/${sampleId}`)
    }
</script>

{#each samples as sample}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="flex flex-row flex-wrap gap-6 py-4 justify-center" on:click={() => handleClick(sample)}>
        <SampleCard
                sampleId={sample}
                machineId={machineId}
                selected={normals.indexOf(sample) !== -1}
                selectModeActive={selectModeActive}
                anomaly={get_anomaly(sample, anomaly_ratios)}
                normalTube={normalTube}
        />
    </div>
{/each}