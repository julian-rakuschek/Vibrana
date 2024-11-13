<script lang="ts">
	import ChunkCard from '@components/ChunkCard.svelte';
	import type { AnomalyMetric, LabelCount } from '@lib/types';
	import DistanceIndicator from '@components/DistanceIndicator.svelte';
	import ChunkTableRow from '@components/lists/ChunkTableRow.svelte';
	import { ColorMode } from '@lib/types';
	import ColorLegend from '@components/atoms/ColorLegend.svelte';
	import { simpleTable } from '@lib/stores';

	export let dataset: string;
	export let subset: string;
	export let chunks: string[];
	export let normals: string[];
	export let anomaly_ratios: AnomalyMetric[];
	export let normalTube: [number, number];
	export let labelCounts: LabelCount[];


	const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
		const res = anomaly_ratios.find(a => a.chunk == needle);
		if (res) return res;
		else return undefined;
	};


</script>
<div class="h-full">
	<div class="flow-root h-full">
		<div class="overflow-x-auto h-full">
			<div class="inline-block min-w-full align-middle h-full overflow-y-scroll">
				<table class="min-w-full divide-y divide-gray-300">
					<thead class="sticky top-0 bg-white z-30">
					<tr>
						<th scope="col" class="text-left text-sm font-semibold text-gray-900 sm:pl-3">Name</th>
						{#if !$simpleTable}
							<th scope="col" class="text-center text-sm font-semibold text-gray-900">Anomalies</th>
							<th scope="col" class="text-center text-sm font-semibold text-gray-900">Labels</th>
						{/if}
						<th scope="col" class="text-left text-sm font-semibold text-gray-900">Time Series / Signal</th>
						<th scope="col" class="text-left text-sm font-semibold text-gray-900">Spectrogram</th>
						<th scope="col" class="text-left text-sm font-semibold text-gray-900">Time Delay Embedding</th>
						{#if !$simpleTable}
							<th scope="col" class="text-left text-sm font-semibold text-gray-900">Seen</th>
							<th scope="col" class="text-center text-sm font-semibold text-gray-900">Anomaly Free</th>
							<th scope="col" class="relative text-center pl-3 pr-4 sm:pr-3">
								<span class="sr-only">Reset Labels</span>
							</th>
						{/if}
					</tr>
					</thead>
					<tbody class="bg-white">
					{#each chunks as chunk}
						<ChunkTableRow
							isNormal={normals.indexOf(chunk) !== -1}
							dataset={dataset}
							subset={subset}
							chunk={chunk}
							labelCount={labelCounts.find(item => item._id === chunk)?.count ?? 0}
							anomaly={get_anomaly(chunk, anomaly_ratios)}
							normalTube={normalTube}
						/>
					{/each}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>
{#if !$simpleTable}
	<div class="fixed bottom-5 right-5 z-10 w-[500px] p-5 shadow-lg bg-white">
		<ColorLegend colorMode={ColorMode.Distance} />
	</div>
{/if}