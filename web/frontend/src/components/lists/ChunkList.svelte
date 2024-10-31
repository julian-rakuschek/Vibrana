<script lang="ts">
    import ChunkCard from "@components/ChunkCard.svelte";
    import type {AnomalyMetric, LabelCount} from "@lib/types";

    export let dataset: string;
    export let subset: string;
    export let chunks: string[];
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let normalTube: [number, number];
    export let labelCounts: LabelCount[];


    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }


</script>
<div>
    {#each chunks as chunk}
        <ChunkCard
                isNormal={normals.indexOf(chunk) !== -1}
                dataset={dataset}
                subset={subset}
                chunk={chunk}
                labelCount={labelCounts.find(item => item._id === chunk)?.count ?? 0}
                anomaly={get_anomaly(chunk, anomaly_ratios)}
                normalTube={normalTube}
        />
    {/each}
</div>
