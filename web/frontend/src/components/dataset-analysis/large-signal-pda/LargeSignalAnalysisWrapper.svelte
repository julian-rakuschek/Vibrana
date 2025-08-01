<script lang="ts">
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {io} from 'socket.io-client';
    import type {ClusterDelta, Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {ColorGenerator} from '@lib/algorithms/colorGenerator';
    import ThreadsControl from '@components/dataset-analysis/large-signal-pda/settings-bar/ThreadsControl.svelte';
    import {DataProvider} from '@lib/dataProvider/dataProvider';
    import {page} from '$app/stores';
    import DataProviderStatus from '@components/dataset-analysis/large-signal-pda/DataProviderStatus.svelte';
    import CenteredLoadingSpinner from '@components/atoms/CenteredLoadingSpinner.svelte';
    import FingerprintDensity from '@components/dataset-analysis/large-signal-pda/FingerprintDensity.svelte';
    import {computeIndexAllocationArray} from '@lib/helper/fingerprintHelper';
    import FingerprintsWrapper
        from '@components/dataset-analysis/large-signal-pda/locations/FingerprintsWrapper.svelte';
    import ClusterOverview from '@components/dataset-analysis/large-signal-pda/overview/ClusterOverview.svelte';
    import ClusteringSettings
        from "@components/dataset-analysis/large-signal-pda/settings-bar/ClusteringSettings.svelte";

    export let dataset = 'hydro';
    export let subset = 'x';
    const w = $page.data.config[dataset].subsets[subset].sliding_window_size;
    const in_memory = $page.data.config[dataset].in_memory;

    const colorGenerator = new ColorGenerator();
    let colorMapping = colorGenerator.getColorDictionary();
    let dataProvider = new DataProvider(dataset, subset, w, in_memory);
    let fingerprints: Fingerprint[] = [];
    let colors: string[] = [];
    let init_load = true;
    let width = 1000;
    let running = false;

    let index_allocation: number[] = new Array(width).fill(-1);
    let label_allocation: number[] = new Array(width).fill(null);

    const socket = io('http://localhost:5000');
    socket.on('connect', () => socket.emit('join', {room: `vibrana:${dataset}:${subset}`}));
    socket.on('message', data => addNewItem(data['new_fingerprint'], data['label_delta']));

    function addNewItem(new_fingerprint: Fingerprint, label_delta: ClusterDelta) {
        new_fingerprint['index'] = fingerprints.length;
        fingerprints = [...fingerprints, new_fingerprint];

        const start = Math.floor((new_fingerprint.start_index / new_fingerprint.max_index) * width);
        const rectangle_width = Math.floor((new_fingerprint.slice_length / new_fingerprint.max_index) * width);

        for (let j = 0; j < rectangle_width; j++) {
            index_allocation[start + j] = new_fingerprint.index;
        }

        for (const labelDeltaElement of label_delta) {
            const color = colorGenerator.getColor(labelDeltaElement.new_label);
            if (labelDeltaElement.index >= colors.length) {
                colors = [...colors, color];
            } else {
                colors[labelDeltaElement.index] = color;
                fingerprints[labelDeltaElement.index].label = labelDeltaElement.new_label;
            }
        }

        for (let i = 0; i < width; i++) {
            if (index_allocation[i] !== -1) {
                label_allocation[i] = fingerprints[index_allocation[i]].label;
            }
        }

        colorMapping = colorGenerator.getColorDictionary();
    }

    async function fetchAndDrawAll() {
        let vectors_query = await ApiRoutes.getFingerprints.fetch({params: {dataset, subset}});
        colors = [];
        for (let i = 0; i < vectors_query.length; i++) {
            vectors_query[i]['index'] = i;
            const color = colorGenerator.getColor(vectors_query[i].label);
            colors = [...colors, color];
        }
        fingerprints = [...vectors_query];
        colorMapping = colorGenerator.getColorDictionary();
        index_allocation = computeIndexAllocationArray(fingerprints, width, -1, false);
        label_allocation = computeIndexAllocationArray(fingerprints, width, null, true);
    }

    onMount(async () => {
        await fetchAndDrawAll();
        init_load = false;
    });

</script>

<div class="flex flex-row w-full gap-10 h-full" bind:clientWidth={width}>
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
                    <p class="bg-indigo-600 text-white rounded-full px-4 pt-0.5 pb-1 text-sm font-semibold">
                        {#if running}running{:else}paused{/if}
                    </p>
                </div>
                <ThreadsControl {dataset} {subset} handleReset={() => fetchAndDrawAll()} handleSingleItem={addNewItem}
                                bind:running/>
            </div>
            <div class="bg-indigo-100 rounded-xl p-4 flex flex-col gap-4 text-indigo-800">
                <p class="font-semibold">Clustering Parameters</p>
                <ClusteringSettings {dataset} {subset} onRecomputeComplete={fetchAndDrawAll}/>
            </div>
        </div>
        <div class="flex flex-col gap-5">
            <!--			<ClusterOverview {width} {fingerprints} {dataProvider} {colorMapping} {index_allocation} {label_allocation} />-->
            <FingerprintsWrapper {width} {dataset} {subset} {fingerprints} {colors} {dataProvider} {index_allocation}
                                 {colorMapping} {label_allocation}/>
            <div>
                <FingerprintDensity {width} {dataset} {subset} {fingerprints}/>
            </div>
        </div>
    {/if}
</div>
