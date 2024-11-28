<script lang="ts">
	import { ApiRoutes } from '@lib/api/ApiRoutes';
	import { useQueryFetch } from '@lib/api/ApiQueries';
	import CenteredLoadingSpinner from '@components/atoms/CenteredLoadingSpinner.svelte';
	import DistanceIndicator from '@components/similarities/DistanceIndicator.svelte';
	import type { AnomalyMetric } from '@lib/types';

	let dataset: string = 'nasa-bearings';
	let subset: string = 'test2';

	const chunkListQuery = useQueryFetch(ApiRoutes.getChunks, { params: { dataset, subset } });
	const normalsQuery = useQueryFetch(ApiRoutes.getNormals, { params: { dataset, subset } }, undefined, undefined, false);
	const labelQuery = useQueryFetch(ApiRoutes.getAllLabels, {
		params: {
			dataset,
			subset
		}
	}, undefined, undefined, false);
	const anomalyRatiosQuery = useQueryFetch(ApiRoutes.getAnomalyRatios, { params: { dataset, subset } });
	const normalTubeQuery = useQueryFetch(ApiRoutes.getNormalTube, { params: { dataset, subset } });

	const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }

</script>

{#if $chunkListQuery.isPending || $normalsQuery.isPending || $normalTubeQuery.isPending || $labelQuery.isPending || $anomalyRatiosQuery.isPending}
	<div class="w-full h-full pt-20">
		<CenteredLoadingSpinner />
	</div>
{/if}

<div class="flex flex-row flex-nowrap">
	{#if $chunkListQuery.isSuccess && $normalsQuery.isSuccess && $normalTubeQuery.isSuccess && $labelQuery.isSuccess && $anomalyRatiosQuery.isSuccess}
	{#each $chunkListQuery.data as chunk, index}
		<div class="flex flex-col shrink-0 w-[150px]">
			<img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail"
                         class={`object-scale-down w-full`}/>
			<div class="w-full h-[20px] flex justify-center">
                <DistanceIndicator ts_length={20000} distances={get_anomaly(chunk, $anomalyRatiosQuery.data).distances_reduced} labels={$labelQuery.data.filter(l => l.chunk === chunk)} normalTube={$normalTubeQuery.data}/>
            </div>
			<p class="text-center font-semibold text-xl">{index}</p>
		</div>
	{/each}
{/if}
</div>
