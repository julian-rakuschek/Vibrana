<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import ProvenanceRendering
        from "@components/dataset-analysis/large-signal-pda/provenance/ProvenanceRendering.svelte";

    export let dataset: string;
    export let subset: string;

    const provenanceQuery = useQueryFetch(ApiRoutes.allProvenance, {params: {dataset, subset}}, undefined, undefined)
</script>

{#if $provenanceQuery.data}
    <ProvenanceRendering provenance_records={$provenanceQuery.data} />
{/if}