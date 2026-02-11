<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import ProvenanceRendering
        from "@components/dataset-analysis/large-signal-pda/provenance/ProvenanceRendering.svelte";

    export let dataset: string;
    export let subset: string;
    export let width: number;

    const provenanceQuery = useQueryFetch(ApiRoutes.allProvenance, {params: {dataset, subset}}, undefined, undefined)
</script>

{#if $provenanceQuery.data}
    <div class="flex flex-row justify-around">
        <ProvenanceRendering provenance_records={$provenanceQuery.data} feature="tde" width={Math.floor(width * 0.4)} />
        <ProvenanceRendering provenance_records={$provenanceQuery.data} feature="psd" width={Math.floor(width * 0.4)} />

    </div>
{/if}