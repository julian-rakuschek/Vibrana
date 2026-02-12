<script lang="ts">
    import {fingerprintMode} from "@lib/stores.js";
    import DataProviderStatus from "@components/clusterAnalysis/settings/DataProviderStatus.svelte";
    import CoverageIndicator from "@components/clusterAnalysis/settings/CoverageIndicator.svelte";
    import ThreadsControl from "@components/clusterAnalysis/settings/ThreadsControl.svelte";
    import ClusteringSettings from "@components/clusterAnalysis/settings/ClusteringSettings.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import type {ClusterDelta, Fingerprint} from "@lib/types";
    import Tooltip from "@components/atoms/Tooltip.svelte";


    interface Props {
        dataset?: string;
        subset?: string;
        dataProvider: DataProvider;
        fingerprints?: Fingerprint[];
        index_allocation: number[];
        label_allocation_tde: number[];
        label_allocation_psd: number[];
        fetchAndDrawAll: () => void;
        addNewItem: (new_fingerprint: Fingerprint, label_delta: ClusterDelta) => void;
    }

    let {
        dataset = 'hydro',
        subset = 'x',
        dataProvider,
        fingerprints = [],
        index_allocation,
        label_allocation_tde,
        label_allocation_psd,
        fetchAndDrawAll,
        addNewItem
    }: Props = $props();

    let running: boolean = $state(false);

    function inkUsed(index_allocation: number[]): number {
        const count = index_allocation.filter(x => x !== -1).length;
        const ink = count / index_allocation.length;
        return Math.round(ink * 10000) / 100
    }
</script>

<div class="w-[350px] flex flex-col shadow-xl shrink-0 p-4 gap-4 h-full rounded-b-xl">
    <p class="self-center text-center text-xl font-bold">Large Signal Analysis</p>
    <DataProviderStatus {dataProvider}/>
    <div class="bg-indigo-100 rounded-xl p-4 flex flex-col gap-4 text-indigo-800">
        <p class="font-semibold">Overview</p>
        <div class="grid grid-cols-4 gap-y-2">
            <p class="col-span-3">Fingerprints:</p>
            <p>{fingerprints.length}</p>
            <p class="col-span-3">Number of Clusters:</p>
            {#if $fingerprintMode === "tde"}
                <p>{(new Set(label_allocation_tde)).size - 1}</p>
            {:else}
                <p>{(new Set(label_allocation_psd)).size - 1}</p>
            {/if}
            <div class="flex flex-row items-center gap-1 col-span-3">
                <span>Coverage:</span>
                <Tooltip color="#303f9f" text="The percentage of data points which have been 'seen' from the entire signal."/>
            </div>
            <CoverageIndicator {dataset} {subset}/>
            <div class="flex flex-row items-center gap-1 col-span-3">
                <span>Ink Used:</span>
                <Tooltip color="#303f9f" text="The percentage of area covered by fingerprints in the timeline visualization. This ratio changes if users zoom into the signal."/>
            </div>
            <p>{inkUsed(index_allocation)}%</p>
        </div>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <div class="bg-indigo-100 rounded-xl p-2 transition hover:bg-indigo-200 border-4 border-solid {$fingerprintMode === 'tde' ? 'border-indigo-800' : 'border-indigo-100'}"
             onclick={() => fingerprintMode.set("tde")}>
            <img src="/tde.png"/>
            <div class="flex flex-row items-center justify-center gap-1">
                <p class="text-center text-indigo-800">Projection</p>
                <Tooltip color="#303f9f" text="The time series is projected into the 2D plane by taking a sliding window view and subsequently applying PCA on it. Strong frequency components lead to circular arrangements within the point cloud."/>
            </div>
        </div>
        <div class="bg-indigo-100 rounded-xl p-2 transition hover:bg-indigo-200 border-4 border-solid {$fingerprintMode === 'psd' ? 'border-indigo-800' : 'border-indigo-100'}"
             onclick={() => fingerprintMode.set("psd")}>
            <img src="/welch.png"/>
            <div class="flex flex-row items-center justify-center gap-1">
                <p class="text-center text-indigo-800">PSD</p>
                <Tooltip color="#303f9f" text="The estimated power spectral density of the signal using Welch's method. The periodogram shows the power distribution across the frequencies."/>
            </div>
        </div>
    </div>
    <div class="bg-indigo-100 rounded-xl p-4 gap-2 flex flex-col text-indigo-800">
        <div class="flex flex-row justify-between">
            <p class="font-semibold">Sampling Control</p>
            {#if running}<p class="bg-green-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">
                running</p>
            {:else}<p class="bg-indigo-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">
                paused</p>{/if}
        </div>
        <ThreadsControl
                {dataset} {subset} handleReset={fetchAndDrawAll} handleSingleItem={addNewItem} bind:running
        />
    </div>
    <div class="bg-indigo-100 rounded-xl p-4 flex flex-col gap-4 text-indigo-800">
        <p class="font-semibold">
            Clustering Parameters ({$fingerprintMode === "tde" ? "Projection" : "PSD"})
        </p>
        <ClusteringSettings
                {dataset} {subset} onRecomputeComplete={fetchAndDrawAll} fingerprintMode={$fingerprintMode}
        />
    </div>
</div>