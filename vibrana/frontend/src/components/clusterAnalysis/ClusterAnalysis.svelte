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
    import ProvenanceWrapper from "@components/clusterAnalysis/provenance/ProvenanceWrapper.svelte";
    import Settings from "@components/clusterAnalysis/settings/Settings.svelte";
    import Header from "@components/clusterAnalysis/Header.svelte";

    interface Props {
        dataset?: string;
        subset?: string;
    }

    let {dataset = 'hydro', subset = 'x'}: Props = $props();
    const in_memory = page.data.config[dataset].loader === "memory";

    let dataProvider = new DataProvider(dataset, subset, in_memory);
    const color_generator_tde = new ColorGenerator();
    const color_generator_psd = new ColorGenerator();
    let color_mapping_tde = $state(color_generator_tde.getColorDictionary());
    let color_mapping_psd = $state(color_generator_psd.getColorDictionary());
    let fingerprints: Fingerprint[] = $state([]);
    let init_load = $state(true);
    let width = $state(1000);
    let zoom_interval: [number, number] = $state([0, 1]);

    let timestamps: number[] = $state(new Array(width).fill(0));
    let index_allocation: number[] = $state(new Array(width).fill(-1));
    let label_allocation_tde: number[] = $state(new Array(width).fill(null));
    let label_allocation_psd: number[] = $state(new Array(width).fill(null));

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
        <div class="flex flex-col grow overflow-shown gap-3" bind:clientWidth={width}>
            <Header {timestamps}/>
            <div>
                <TimelineFingerprintRepresentatives
                        {width} index_allocation={$state.snapshot(index_allocation)}
                        fingerprints={$state.snapshot(fingerprints)}
                        {dataProvider} {zoom_interval}
                        colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                />
                <ClusterTimelineWrapper
                        {width} {dataset} {subset} fingerprints={$state.snapshot(fingerprints)}
                        {dataProvider} index_allocation={$state.snapshot(index_allocation)} {timestamps}
                        label_allocation={$fingerprintMode === "tde" ? $state.snapshot(label_allocation_tde) : $state.snapshot(label_allocation_psd)}
                        colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                        bind:zoom_interval
                />
            </div>
            <div class="shadow-[0_0_10px_rgba(0,0,0,0.25)] pb-2">
                <ZoomIndicator
                        {width} fingerprints={$state.snapshot(fingerprints)} {zoom_interval}
                        feature={$fingerprintMode} reset_zoom={() => zoom_interval = [0, 1]}
                        colorMapping={$fingerprintMode === "tde" ? color_mapping_tde : color_mapping_psd}
                />
            </div>
            <div class="shadow-[0_0_10px_rgba(0,0,0,0.25)] mt-5">
                <Uncertainty {width} {dataset} {subset} fingerprints={$state.snapshot(fingerprints)} {zoom_interval}/>
            </div>
            <div class="shadow-[0_0_10px_rgba(0,0,0,0.25)] mt-5 mb-5 pt-2">
                <ProvenanceWrapper {width} {dataset} {subset}/>
            </div>
        </div>
    {/if}
</div>
