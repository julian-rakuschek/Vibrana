<script lang="ts">
    import ChunkCard from "@components/ChunkCard.svelte";
    import type {AnomalyMetric, LabelCount} from "@lib/types";
    import DistanceIndicator from "@components/DistanceIndicator.svelte";
    import ChunkTableRow from "@components/lists/ChunkTableRow.svelte";

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
<div class="px-4 sm:px-6 lg:px-8">
    <div class="flow-root">
        <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8 mt-5">
            <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead>
                    <tr>
                        <th scope="col" class="text-left text-sm font-semibold text-gray-900 sm:pl-3">Name</th>
                        <th scope="col" class="text-center text-sm font-semibold text-gray-900">Anomalies</th>
                        <th scope="col" class="text-center text-sm font-semibold text-gray-900">Labels</th>
                        <th scope="col" class="text-left text-sm font-semibold text-gray-900">Time Series / Signal</th>
                        <th scope="col" class="text-left text-sm font-semibold text-gray-900">Spectrogram</th>
                        <th scope="col" class="text-left text-sm font-semibold text-gray-900">Time Delay Embedding</th>
                        <th scope="col" class="text-left text-sm font-semibold text-gray-900">Seen</th>
                        <th scope="col" class="text-center text-sm font-semibold text-gray-900">Anomaly Free</th>
                        <th scope="col" class="relative text-center py-3.5 pl-3 pr-4 sm:pr-3">
                            <span class="sr-only">Reset Labels</span>
                        </th>
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
