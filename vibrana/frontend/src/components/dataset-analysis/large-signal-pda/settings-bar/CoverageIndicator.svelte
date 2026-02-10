<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import type {Provenance} from "@lib/types";

    export let dataset: string;
    export let subset: string;

    const provenanceQuery = useQueryFetch(ApiRoutes.latestProvenance, {params: {dataset, subset}}, undefined, undefined)

    function computeCoverage(prov: Provenance) {
        const cov = prov.coverage / prov.signal_length;
        return Math.round(cov * 10000) / 100
    }
</script>

{#if $provenanceQuery.data}
    <p>{computeCoverage($provenanceQuery.data)}%</p>
{/if}