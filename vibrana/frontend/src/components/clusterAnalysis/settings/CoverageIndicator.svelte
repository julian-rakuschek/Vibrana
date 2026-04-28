<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";

    interface Props {
        dataset: string;
        subset: string;
    }

    let { dataset, subset }: Props = $props();
    const coverageQuery = useQueryFetch(ApiRoutes.getCoverage, {
        params: {dataset, subset}
    });

</script>

{#if coverageQuery.isPending}
    <p>Loading...</p>
{:else if coverageQuery.isError}
    <p>Error</p>
{:else}
    <p>{coverageQuery.data.toFixed(2)}%</p>
{/if}
