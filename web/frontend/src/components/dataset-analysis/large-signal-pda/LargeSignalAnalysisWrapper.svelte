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
    import FingerprintDensity from '@components/dataset-analysis/large-signal-pda/FingerprintDensity.svelte';
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

    export let dataset = 'hydro';
    export let subset = 'x';
    const w = $page.data.config[dataset].subsets[subset].sliding_window_size;
    const in_memory = $page.data.config[dataset].in_memory;

    const colorGenerator = new ColorGenerator();
    let colorMapping = colorGenerator.getColorDictionary();
    let dataProvider = new DataProvider(dataset, subset, w, in_memory);
    let fingerprints: Fingerprint[] = [];
    let init_load = true;
    let width = 1000;
    let running = false;
    let zoom_interval: [number, number] = [0, 1];

    let index_allocation: number[] = new Array(width).fill(-1);
    let label_allocation: number[] = new Array(width).fill(null);

    const socket = io('http://localhost:5000');
    socket.on('connect', () => socket.emit('join', {room: `vibrana:${dataset}:${subset}`}));
    socket.on('message', data => addNewItem(data['new_fingerprint'], data['label_delta']));

    function addNewItem(new_fingerprint: Fingerprint, label_delta: ClusterDelta) {
        new_fingerprint['index'] = fingerprints.length;
        fingerprints = [...fingerprints, new_fingerprint];

        index_allocation = updateIndexAllocationArray(index_allocation, new_fingerprint, zoom_interval);

        for (const labelDeltaElement of label_delta) {
            colorGenerator.getColor(labelDeltaElement.new_label);
            fingerprints[labelDeltaElement.index].label = labelDeltaElement.new_label;
        }

        for (let i = 0; i < width; i++) {
            if (index_allocation[i] !== -1) {
                label_allocation[i] = fingerprints[index_allocation[i]].label;
            }
        }

        colorMapping = colorGenerator.getColorDictionary();
    }

    async function fetchAndDrawAll() {
        zoom_interval = [0, 1];
        let vectors_query = await ApiRoutes.getFingerprints.fetch({params: {dataset, subset}});
        for (let i = 0; i < vectors_query.length; i++) {
            vectors_query[i]['index'] = i;
            colorGenerator.getColor(vectors_query[i].label);
        }
        fingerprints = [...vectors_query];
        colorMapping = colorGenerator.getColorDictionary();
        index_allocation = computeIndexAllocationArray(fingerprints, width, zoom_interval);
        label_allocation = computeLabelAllocationArray(fingerprints, width, zoom_interval);
    }

    onMount(async () => {
        await fetchAndDrawAll();
        init_load = false;
    });

    function updateAllocationArrays(width: number, zoom_interval: [number, number]) {
        index_allocation = computeIndexAllocationArray(fingerprints, width, zoom_interval);
        label_allocation = computeLabelAllocationArray(fingerprints, width, zoom_interval);
    }

    $: updateAllocationArrays(width, zoom_interval);

</script>

<div class="flex flex-row w-full gap-10 h-full pr-10">
    {#if init_load}
        <CenteredLoadingSpinner/>
    {:else}
        <div class="w-[350px] flex flex-col shadow-xl shrink-0 p-4 gap-4 h-full">
            <p class="self-center text-center text-xl font-bold">Large Signal Analysis</p>
            <DataProviderStatus {dataProvider}/>
            <div class="bg-indigo-100 rounded-xl p-4 flex flex-col gap-4 text-indigo-800">
                <p class="font-semibold">Overview</p>
                <div class="grid grid-cols-4 gap-y-2">
                    <p class="col-span-3">Fingerprints:</p>
                    <p>{fingerprints.length}</p>
                    <p class="col-span-3">Number of Clusters:</p>
                    <p>{(new Set(label_allocation)).size}</p>
                </div>
            </div>
            <div class="bg-indigo-100 rounded-xl p-4 gap-2 flex flex-col text-indigo-800">
                <div class="flex flex-row justify-between">
                    <p class="font-semibold">Computing Control</p>
                    {#if running}<p class="bg-green-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">running</p>
                    {:else}<p class="bg-indigo-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">paused</p>{/if}
                </div>
                <ThreadsControl {dataset} {subset} handleReset={() => fetchAndDrawAll()} handleSingleItem={addNewItem}
                                bind:running/>
            </div>
            <div class="bg-indigo-100 rounded-xl p-4 flex flex-col gap-4 text-indigo-800">
                <p class="font-semibold">Clustering Parameters</p>
                <ClusteringSettings {dataset} {subset} onRecomputeComplete={fetchAndDrawAll}/>
            </div>
        </div>
        <div class="flex flex-col grow overflow-hidden" bind:clientWidth={width}>
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

            </div>

            {#key width}
                <TimelineFingerprintRepresentatives
                        {width} {index_allocation} {fingerprints}
                        {dataProvider} {colorMapping} {zoom_interval}
                />
                <FingerprintsWrapper
                        {width} {dataset} {subset} {fingerprints}
                        {dataProvider} {index_allocation}
                        {colorMapping} {label_allocation}
                        bind:zoom_interval
                />
                <p class="font-semibold mt-5">Zooming Location</p>
                <ZoomIndicator {width} {fingerprints} {colorMapping} {zoom_interval} />
                <div class="flex">
    <p on:click={() => zoom_interval = [0, 1]} class="text-sm text-black/70 hover:text-black/90 cursor-default border-b-2 border-dotted border-black/70 hover:border-black/90">Reset Zoom</p>
</div>
                <div>
                    <p class="font-semibold mt-5 mb-2">Fingerprint Aging and Density</p>
                    <FingerprintDensity {width} {dataset} {subset} {fingerprints} {zoom_interval}/>
                    <div class="w-[500px]">
                        <ColorLegend colorMode={ColorMode.Age}/>
                    </div>
                </div>
            {/key}
        </div>
    {/if}
</div>
