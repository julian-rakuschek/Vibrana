<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import ProvenanceRendering
        from "@components/clusterAnalysis/provenance/ProvenanceRendering.svelte";

    interface Props {
        dataset: string;
        subset: string;
        width: number;
    }

    let { dataset, subset, width }: Props = $props();

    const provenanceQuery = useQueryFetch(ApiRoutes.allProvenance, {params: {dataset, subset}}, undefined, undefined)
</script>

{#if provenanceQuery.data}
    <p class="text-center font-semibold">Cluster Evolution Over Time</p>
    <div class="flex flex-row justify-around mb-5">
        <ProvenanceRendering provenance_records={provenanceQuery.data} feature="tde" width={Math.floor(width * 0.45)} />
        <div class="mt-5 grow flex flex-col justify-center items-center" style="height: {provenanceQuery.data.length * 10}px">
            <p>Recent</p>
            <div class="grow w-1 bg-black/20">

            </div>
            <p>Old</p>
        </div>
        <ProvenanceRendering provenance_records={provenanceQuery.data} feature="psd" width={Math.floor(width * 0.45)} />
    </div>
{/if}