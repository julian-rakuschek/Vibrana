<script lang="ts">
    import ChunkCard from "@components/ChunkCard.svelte";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {goto} from "$app/navigation";
    import {useQueryClient} from "@tanstack/svelte-query";
    import type {AnomalyMetric} from "@lib/types";
    import {getContext} from "svelte";
    import {sessionToggleNormal} from "@lib/helper/sessionStorageHelper";

    export let dataset: string;
    export let subset: string;
    export let chunks: string[];
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let selectModeActive: boolean;
    export let normalTube: [number, number];

    const client = useQueryClient()

    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }

    const {ro} = getContext("ro") as { ro: boolean }

    const handleClick = async (chunk: string) => {
        if (selectModeActive && normals) {
            if (ro) sessionToggleNormal(dataset, subset)
            else{
                if (normals.indexOf(chunk) === -1) {
                    await ApiRoutes.addNormal.fetch({params: {dataset, subset, chunk}})
                } else {
                    await ApiRoutes.removeNormal.fetch({params: {dataset, subset, chunk}})
                }
            }
            await client.invalidateQueries();
        }
        else goto(`/datasets/${dataset}/${subset}/${chunk}`)
    }
</script>

{#each chunks as chunk}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="flex flex-row flex-wrap gap-6 py-4 justify-center" on:click={() => handleClick(chunk)}>
        <ChunkCard
                dataset={dataset}
                subset={subset}
                chunk={chunk}
                selected={normals.indexOf(chunk) !== -1}
                selectModeActive={selectModeActive}
                anomaly={get_anomaly(chunk, anomaly_ratios)}
                normalTube={normalTube}
        />
    </div>
{/each}