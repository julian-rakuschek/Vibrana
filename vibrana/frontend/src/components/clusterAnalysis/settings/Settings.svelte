<script lang="ts">
    import {fingerprintMode} from "@lib/stores.js";
    import DataProviderStatus from "@components/clusterAnalysis/settings/DataProviderStatus.svelte";
    import CoverageIndicator from "@components/clusterAnalysis/settings/CoverageIndicator.svelte";
    import ThreadsControl from "@components/clusterAnalysis/settings/ThreadsControl.svelte";
    import ClusteringSettings from "@components/clusterAnalysis/settings/ClusteringSettings.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import type {ClusterDelta, Fingerprint} from "@lib/types";

    export let dataset = 'hydro';
    export let subset = 'x';
    export let dataProvider: DataProvider;
    export let fingerprints: Fingerprint[] = [];
    export let index_allocation: number[];
    export let label_allocation_tde: number[];
    export let label_allocation_psd: number[];

    export let fetchAndDrawAll: () => void;
    export let addNewItem: (new_fingerprint: Fingerprint, label_delta: ClusterDelta) => void;

    let running: boolean = false;

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
            <p class="col-span-3">Coverage:</p>
            <CoverageIndicator {dataset} {subset}/>
            <p class="col-span-3">Ink Used:</p>
            <p>{inkUsed(index_allocation)}%</p>
        </div>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <div class="bg-indigo-100 rounded-xl p-2 transition hover:bg-indigo-200 border-4 border-solid {$fingerprintMode === 'tde' ? 'border-indigo-800' : 'border-indigo-100'}"
             on:click={() => fingerprintMode.set("tde")}>
            <img src="/tde.png"/>
            <p class="text-center text-indigo-800">Projection</p>
        </div>
        <div class="bg-indigo-100 rounded-xl p-2 transition hover:bg-indigo-200 border-4 border-solid {$fingerprintMode === 'psd' ? 'border-indigo-800' : 'border-indigo-100'}"
             on:click={() => fingerprintMode.set("psd")}>
            <img src="/welch.png"/>
            <p class="text-center text-indigo-800">PSD</p>
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