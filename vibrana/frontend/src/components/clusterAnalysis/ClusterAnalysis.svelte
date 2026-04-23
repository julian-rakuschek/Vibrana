<script lang="ts">
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {io} from 'socket.io-client';
    import {type ClusterDelta, type Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {ColorGenerator} from '@lib/algorithms/colorGenerator';
    import {DataProvider} from '@lib/dataProvider/dataProvider';
    import {page} from '$app/state';
    import CenteredLoadingSpinner from '@components/atoms/CenteredLoadingSpinner.svelte';
    import Uncertainty from '@components/clusterAnalysis/uncertainty/Uncertainty.svelte';
    import {
        computeIndexAllocationArray,
        computeLabelAllocationArray,
        updateIndexAllocationArray
    } from '@lib/helper/fingerprintHelper';
    import ClusterTimelineWrapper from '@components/clusterAnalysis/clusterTimeline/ClusterTimeline.svelte';
    import TimelineFingerprintRepresentatives
        from "@components/clusterAnalysis/clusterTimeline/TimelineFingerprintRepresentatives.svelte";
    import ZoomIndicator from "@components/clusterAnalysis/clusterTimeline/ZoomIndicator.svelte";
    import {fingerprintMode} from "@lib/stores";
    import {useQueryClient} from "@tanstack/svelte-query";
    import Settings from "@components/clusterAnalysis/settings/Settings.svelte";
    import Header from "@components/clusterAnalysis/Header.svelte";
    import {AVLTree} from "avl";
    import IntervalTree from 'node-interval-tree'
    import ZoomIndicatorV2 from "@components/clusterAnalysis/clusterTimeline/ZoomIndicatorV2.svelte";

    interface Props {
        dataset?: string;
        subset?: string;
    }

    let {dataset = 'hydro', subset = 'x'}: Props = $props();
    const in_memory = page.data.config[dataset].loader === "memory";

    let dataProvider = new DataProvider(dataset, subset, in_memory);
    const color_generator_tde = new ColorGenerator();
    const color_generator_psd = new ColorGenerator();
    const fp_tree = new AVLTree<number, Fingerprint>();
    let fp_interval_tree = new IntervalTree<Fingerprint>();

    let color_mapping_tde = $state(color_generator_tde.getColorDictionary());
    let color_mapping_psd = $state(color_generator_psd.getColorDictionary());
    let fingerprints: Fingerprint[] = $state([]);
    let init_load = $state(true);
    let width = $state(1000);
    let zoom_interval: [number, number] = $state([0, 1]);
    let fingerprintRepresentatives: TimelineFingerprintRepresentatives = $state();

    let timestamps: number[] = $state(new Array(width).fill(0));
    let index_allocation: number[] = $state(new Array(width).fill(-1));
    let label_allocation_tde: number[] = $state(new Array(width).fill(null));
    let label_allocation_psd: number[] = $state(new Array(width).fill(null));

    const socket = io('http://localhost:5000');
    socket.on('connect', () => socket.emit('join', {room: `vibrana:${dataset}:${subset}`}));
    socket.on('message', data => addNewItem(data['new_fingerprint'], data['labels']));

    const client = useQueryClient()

    async function addNewItem(new_fingerprint: Fingerprint, labels: ClusterDelta) {
        const nextFingerprints = [...fingerprints, {...new_fingerprint, index: fingerprints.length}].map((fp, i) => ({
            ...fp,
            label: {
                ...fp.label,
                tde: labels.tde[i] ?? fp.label.tde,
                psd: labels.psd[i] ?? fp.label.psd
            }
        }));

        labels.tde.forEach(label => color_generator_tde.getColor(label));
        labels.psd.forEach(label => color_generator_psd.getColor(label));

        fingerprints = nextFingerprints;
        index_allocation = computeIndexAllocationArray(fingerprints, width, zoom_interval);
        label_allocation_tde = computeLabelAllocationArray(fingerprints, width, zoom_interval, "tde");
        label_allocation_psd = computeLabelAllocationArray(fingerprints, width, zoom_interval, "psd");

        color_mapping_tde = {...color_generator_tde.getColorDictionary()};
        color_mapping_psd = {...color_generator_psd.getColorDictionary()};

        // necessary to rebuild entire tree, because clustering results may change across many instances
        fp_tree.clear();
        fp_interval_tree = new IntervalTree<Fingerprint>();
        for (const nextFingerprint of nextFingerprints) {
            fp_tree.insert(nextFingerprint.start_index, nextFingerprint);
            fp_interval_tree.insert(nextFingerprint.start_index, nextFingerprint.start_index + nextFingerprint.slice_length, nextFingerprint);
        }

        await client.invalidateQueries();

        if (fingerprintRepresentatives) {
            fingerprintRepresentatives.choose_fingerprint_indices(index_allocation, true, fingerprints);
        }
    }

    async function fetchAndDrawAll() {
        zoom_interval = [0, 1];
        let vectors_query = await ApiRoutes.getFingerprints.fetch({params: {dataset, subset}});
        fp_tree.clear();
        fp_interval_tree = new IntervalTree<Fingerprint>();
        for (let i = 0; i < vectors_query.length; i++) {
            vectors_query[i]['index'] = i;
            color_generator_tde.getColor(vectors_query[i].label.tde);
            color_generator_psd.getColor(vectors_query[i].label.psd);
            fp_tree.insert(vectors_query[i].start_index, vectors_query[i]);
            fp_interval_tree.insert(vectors_query[i].start_index, vectors_query[i].start_index + vectors_query[i].slice_length, vectors_query[i]);
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

    $effect(() => {
        updateAllocationArrays(width, zoom_interval);
    });

</script>

<div class="flex flex-row w-full gap-10 pr-10">
    {#if init_load}
        <CenteredLoadingSpinner/>
    {:else}
        <Settings
                {dataset} {subset} {fingerprints}
                {dataProvider} {index_allocation} {label_allocation_tde} {label_allocation_psd}
                {fetchAndDrawAll} {addNewItem}
        />
        {#if fingerprints.length === 0}
            <div class="h-full grow grid place-items-center">
                <p class="text-center italic text-xl">No fingerprint has been computed so far. <br/>Click the "Single
                    Step" button to get started.</p>
            </div>
        {:else}
            <div class="flex flex-col grow overflow-shown gap-3" bind:clientWidth={width}>
                <Header {timestamps}/>
                <div>
                    <ZoomIndicatorV2 {width} {dataProvider} reset_zoom={() => zoom_interval = [0, 1]} bind:zoom_interval {fp_tree} {fp_interval_tree}
                                     colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd} />

                </div>
                <div>
                    <ClusterTimelineWrapper
                            {width} {dataset} {subset} fingerprints={$state.snapshot(fingerprints)}
                            {dataProvider} {fp_tree} {fp_interval_tree} index_allocation={$state.snapshot(index_allocation)} {timestamps}
                            label_allocation={$fingerprintMode === "tde" ? $state.snapshot(label_allocation_tde) : $state.snapshot(label_allocation_psd)}
                            colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                            bind:zoom_interval
                    />
                    {#key width}
                        <TimelineFingerprintRepresentatives
                                {width} index_allocation={$state.snapshot(index_allocation)}
                                fingerprints={fingerprints}
                                {dataProvider} {zoom_interval}
                                colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                                bind:this={fingerprintRepresentatives}
                        />
                    {/key}
                </div>
            </div>
        {/if}
    {/if}
</div>
