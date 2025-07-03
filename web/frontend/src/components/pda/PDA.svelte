<script lang="ts">
	import { useQueryFetch } from '@lib/api/ApiQueries';
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import PDAThreadsControl from '@components/pda/PDAThreadsControl.svelte';
	import PDASocket from '@components/pda/PDASocket.svelte';
	import PDAVis from "@components/pda/PDAVis.svelte";

	export let dataset = 'hydro';
	export let subset = 'x';
	const vectorsQuery = useQueryFetch(ApiRoutes.getVectors, { params: { dataset, subset } });

</script>


<div class="grid grid-cols-3 px-10">
	<PDAThreadsControl dataset={dataset} subset={subset} />
	<p class="self-center text-center text-xl font-bold">Long Signal Analysis</p>
	<p class="self-center text-right">{#if $vectorsQuery.data && $vectorsQuery.isSuccess}{$vectorsQuery.data.length} Fingerprints{/if}</p>
</div>


{#if $vectorsQuery.data && $vectorsQuery.isSuccess}
	<PDAVis vectors={$vectorsQuery.data} />
{/if}

<PDASocket />