<script lang="ts">
	import { useQueryFetch } from '@lib/api/ApiQueries';
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import PDAThreadsControl from '@components/pda/PDAThreadsControl.svelte';
	import PDASocket from '@components/pda/PDASocket.svelte';

	export let dataset = 'hydro';
	export let subset = 'x';
	const vectorsQuery = useQueryFetch(ApiRoutes.getVectors, { params: { dataset, subset } });

</script>

<p>PDA</p>

<PDAThreadsControl dataset={dataset} subset={subset} />

{#if $vectorsQuery.data && $vectorsQuery.isSuccess}
	<p>{$vectorsQuery.data.length}</p>
{/if}

<PDASocket />