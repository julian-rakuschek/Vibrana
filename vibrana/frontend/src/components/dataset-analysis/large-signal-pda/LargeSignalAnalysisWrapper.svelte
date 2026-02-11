<script lang="ts">
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {io} from 'socket.io-client';
    import {type ClusterDelta, ColorMode, type Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {ColorGenerator} from '@lib/algorithms/colorGenerator';
    import ThreadsControl from '@components/dataset-analysis/large-signal-pda/settings-bar/ThreadsControl.svelte';
    import {DataProvider} from '@lib/dataProvider/dataProvider';
    import {page} from '$app/stores';
    import DataProviderStatus from '@components/dataset-analysis/large-signal-pda/DataProviderStatus.svelte';
    import CenteredLoadingSpinner from '@components/atoms/CenteredLoadingSpinner.svelte';
    import Uncertainty from '@components/dataset-analysis/large-signal-pda/Uncertainty.svelte';
    import {
        computeIndexAllocationArray,
        computeLabelAllocationArray,
        updateIndexAllocationArray
    } from '@lib/helper/fingerprintHelper';
    import FingerprintsWrapper
        from '@components/dataset-analysis/large-signal-pda/locations/FingerprintsWrapper.svelte';
    import ClusteringSettings
        from "@components/dataset-analysis/large-signal-pda/settings-bar/ClusteringSettings.svelte";
    import TimelineFingerprintRepresentatives
        from "@components/dataset-analysis/large-signal-pda/TimelineFingerprintRepresentatives.svelte";
    import MouseButtonLeft from "@components/icons/MouseButtonLeft.svelte";
    import MouseButtonRight from "@components/icons/MouseButtonRight.svelte";
    import ColorLegend from "@components/atoms/ColorLegend.svelte";
    import MouseScroll from "@components/icons/MouseScroll.svelte";
    import ZoomIndicator from "@components/dataset-analysis/large-signal-pda/locations/ZoomIndicator.svelte";
    import {fingerprintMode} from "@lib/stores";
    import {humanTimeSpan} from "@lib/helper/util";
    import CoverageIndicator from "@components/dataset-analysis/large-signal-pda/settings-bar/CoverageIndicator.svelte";
    import {useQueryClient} from "@tanstack/svelte-query";
    import ProvenanceWrapper from "@components/dataset-analysis/large-signal-pda/provenance/ProvenanceWrapper.svelte";

    export let dataset = 'hydro';
    export let subset = 'x';
    const in_memory = $page.data.config[dataset].loader === "memory";

    let dataProvider = new DataProvider(dataset, subset, in_memory);
    const color_generator_tde = new ColorGenerator();
    const color_generator_psd = new ColorGenerator();
    let color_mapping_tde = color_generator_tde.getColorDictionary();
    let color_mapping_psd = color_generator_psd.getColorDictionary();
    let fingerprints: Fingerprint[] = [];
    let init_load = true;
    let width = 1000;
    let running = false;
    let zoom_interval: [number, number] = [0, 1];

    let timestamps: number[] = new Array(width).fill(0);
    let index_allocation: number[] = new Array(width).fill(-1);
    let label_allocation_tde: number[] = new Array(width).fill(null);
    let label_allocation_psd: number[] = new Array(width).fill(null);

    const socket = io('http://localhost:5000');
    socket.on('connect', () => socket.emit('join', {room: `vibrana:${dataset}:${subset}`}));
    socket.on('message', data => addNewItem(data['new_fingerprint'], data['labels']));

    const client = useQueryClient()

    async function addNewItem(new_fingerprint: Fingerprint, labels: ClusterDelta) {
        console.log(new_fingerprint, labels)
        new_fingerprint['index'] = fingerprints.length;
        fingerprints = [...fingerprints, new_fingerprint];

        index_allocation = updateIndexAllocationArray(index_allocation, new_fingerprint, zoom_interval);

        console.log(index_allocation)
        for (let i = 0; i < labels.tde.length; i++) {
            color_generator_tde.getColor(labels.tde[i]);
            fingerprints[i].label.tde = labels.tde[i];
        }
        for (let i = 0; i < labels.psd.length; i++) {
            color_generator_psd.getColor(labels.psd[i]);
            fingerprints[i].label.psd = labels.psd[i];
        }

        for (let i = 0; i < width; i++) {
            if (index_allocation[i] !== -1) {
                label_allocation_tde[i] = fingerprints[index_allocation[i]].label.tde;
                label_allocation_psd[i] = fingerprints[index_allocation[i]].label.psd;
            }
        }

        color_mapping_tde = color_generator_tde.getColorDictionary();
        color_mapping_psd = color_generator_psd.getColorDictionary();
        await client.invalidateQueries();
    }

    async function fetchAndDrawAll() {
        zoom_interval = [0, 1];
        let vectors_query = await ApiRoutes.getFingerprints.fetch({params: {dataset, subset}});
        for (let i = 0; i < vectors_query.length; i++) {
            vectors_query[i]['index'] = i;
            color_generator_tde.getColor(vectors_query[i].label.tde);
            color_generator_psd.getColor(vectors_query[i].label.psd);
        }
        fingerprints = [...vectors_query];
        color_mapping_tde = color_generator_tde.getColorDictionary();
        color_mapping_psd = color_generator_psd.getColorDictionary();
        index_allocation = computeIndexAllocationArray(fingerprints, width, zoom_interval);
        label_allocation_tde = computeLabelAllocationArray(fingerprints, width, zoom_interval, "tde");
        label_allocation_psd = computeLabelAllocationArray(fingerprints, width, zoom_interval, "psd");
        timestamps = await dataProvider.get_timestamps(zoom_interval, width);
        await client.invalidateQueries();
    }

    function inkUsed(index_allocation: number[]): number {
        const count = index_allocation.filter(x => x !== -1).length;
        const ink = count / index_allocation.length;
        return Math.round(ink * 10000) / 100
    }

    onMount(async () => {
        await fetchAndDrawAll();
        init_load = false;
    });

    async function updateAllocationArrays(width: number, zoom_interval: [number, number]) {
        index_allocation = computeIndexAllocationArray(fingerprints, width, zoom_interval);
        label_allocation_tde = computeLabelAllocationArray(fingerprints, width, zoom_interval, "tde");
        label_allocation_psd = computeLabelAllocationArray(fingerprints, width, zoom_interval, "psd");
        timestamps = await dataProvider.get_timestamps(zoom_interval, width);
    }

    $: updateAllocationArrays(width, zoom_interval);

</script>

<div class="flex flex-row w-full gap-10 pr-10">
    {#if init_load}
        <CenteredLoadingSpinner/>
    {:else}
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
                    <CoverageIndicator {dataset} {subset} />
                    <p class="col-span-3">Ink Used:</p>
                    <p>{inkUsed(index_allocation)}%</p>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-indigo-100 rounded-xl p-2 transition hover:bg-indigo-200 border-4 border-solid {$fingerprintMode === 'tde' ? 'border-indigo-800' : 'border-indigo-100'}" on:click={() => fingerprintMode.set("tde")}>
                    <img src="/tde.png" />
                    <p class="text-center text-indigo-800">Projection</p>
                </div>
                <div class="bg-indigo-100 rounded-xl p-2 transition hover:bg-indigo-200 border-4 border-solid {$fingerprintMode === 'psd' ? 'border-indigo-800' : 'border-indigo-100'}" on:click={() => fingerprintMode.set("psd")}>
                    <img src="/welch.png" />
                    <p class="text-center text-indigo-800">PSD</p>
                </div>
            </div>
            <div class="bg-indigo-100 rounded-xl p-4 gap-2 flex flex-col text-indigo-800">
                <div class="flex flex-row justify-between">
                    <p class="font-semibold">Sampling Control</p>
                    {#if running}<p class="bg-green-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">running</p>
                    {:else}<p class="bg-indigo-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">paused</p>{/if}
                </div>
                <ThreadsControl {dataset} {subset} handleReset={() => fetchAndDrawAll()} handleSingleItem={addNewItem}
                                bind:running/>
            </div>
            <div class="bg-indigo-100 rounded-xl p-4 flex flex-col gap-4 text-indigo-800">
                <p class="font-semibold">
                    Clustering Parameters ({$fingerprintMode === "tde" ? "Projection" : "PSD"})
                </p>
                <ClusteringSettings {dataset} {subset} onRecomputeComplete={fetchAndDrawAll} fingerprintMode={$fingerprintMode}/>
            </div>
        </div>
        <div class="flex flex-col grow overflow-shown" bind:clientWidth={width}>
            <div class="gap-2 flex flex-col pb-3">
                <p class="font-semibold">Fingerprint Locations and Clusters</p>
                <p class="text-sm">
                    The visualization shows the location of computed fingerprints across the signal.
                    Each fingerprint is assigned to a cluster, which is shown through the colors.
                    Since the algorithm computes one fingerprint at a time, users may steer the algorithm by defining
                    intervals.
                    The algorithm will subsequently only compute fingerprints in defined intervals.
                    If no interval is defined, a random index is sampled.
                    For large signals, users may zoom into the signal.
                </p>
                <div class="flex flex-col px-3">
                    <div class="flex flex-row items-center text-black/70 text-md">
                        <MouseButtonLeft/>
                        & drag: Add Interval
                    </div>
                    <div class="flex flex-row items-center text-black/70 text-md">
                        <MouseButtonRight/>
                        & drag: Remove (Partial) Interval
                    </div>
                    <div class="flex flex-row items-center text-black/70 text-md">
                        <MouseScroll/>
                        : Zoom
                    </div>
                </div>
                <p class="text-center italic"><span class="font-semibold text-indigo-700">Time Span:</span> {humanTimeSpan(timestamps)}</p>
            </div>

            {#key width}
                <TimelineFingerprintRepresentatives
                        {width} {index_allocation} {fingerprints}
                        {dataProvider} {zoom_interval}
                        colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                />
                <FingerprintsWrapper
                        {width} {dataset} {subset} {fingerprints}
                        {dataProvider} {index_allocation} {timestamps}
                        label_allocation={$fingerprintMode === "tde" ? label_allocation_tde : label_allocation_psd}
                        colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                        bind:zoom_interval
                />
                <p class="font-semibold mt-5">Zooming Location</p>
                <ZoomIndicator
                        {width} {fingerprints} {zoom_interval} feature={$fingerprintMode}
                        colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                />
                <div class="flex">
    <p on:click={() => zoom_interval = [0, 1]} class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">Reset Zoom</p>
</div>
                <div>
                    <div class="w-full flex flex-row justify-between">
                        <p class="font-semibold mt-5 mb-2">Uncertainty</p>
                        <div class="w-[500px]">
                        <ColorLegend colorMode={ColorMode.Uncertainty}/>
                    </div>
                    </div>
                    <Uncertainty {width} {dataset} {subset} {fingerprints} {zoom_interval}/>

                    <ProvenanceWrapper {width} {dataset} {subset} />
                </div>
            {/key}
        </div>
    {/if}
</div>
