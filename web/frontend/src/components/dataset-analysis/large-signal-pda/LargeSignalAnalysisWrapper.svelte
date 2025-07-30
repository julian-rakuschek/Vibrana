<script lang="ts">
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {io} from 'socket.io-client';
    import type {ClusterHistogram, Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {ColorGenerator} from '@lib/algorithms/colorGenerator';
    import ClusterOverview from "@components/dataset-analysis/large-signal-pda/visualizations/ClusterOverview.svelte";
    import FingerprintLocations
        from "@components/dataset-analysis/large-signal-pda/visualizations/FingerprintLocations.svelte";
    import ProbabilitySculpting
        from "@components/dataset-analysis/large-signal-pda/steering/ProbabilitySculpting.svelte";
    import ClusterDistribution
        from "@components/dataset-analysis/large-signal-pda/visualizations/ClusterDistribution.svelte";
    import ThreadsControl from "@components/dataset-analysis/large-signal-pda/steering/ThreadsControl.svelte";
    import {DataProvider} from "@lib/dataProvider/dataProvider";
    import {page} from '$app/stores';
    import DataProviderStatus from "@components/dataset-analysis/large-signal-pda/DataProviderStatus.svelte";

    export let dataset = 'hydro';
    export let subset = 'x';
    const w = $page.data.config[dataset].subsets[subset].sliding_window_size;
    const in_memory = $page.data.config[dataset].in_memory;

    const colorGenerator = new ColorGenerator();
    let dataProvider = new DataProvider(dataset, subset, w, in_memory);
    let loading = true;
    let fingerprints: Fingerprint[] = [];
    let colors: string[] = [];
    let cluster_histogram: ClusterHistogram = [];

    const socket = io('http://localhost:5000');
    socket.on('connect', () => socket.emit('join', {room: `vibrana:${dataset}:${subset}`}));
    socket.on('message', data => addNewItem(data["new_fingerprint"], data["label_delta"]));

    function addNewItem(new_fingerprint: Fingerprint, label_delta: { index: number; new_label: number }[]) {
        new_fingerprint["index"] = fingerprints.length;
        fingerprints = [...fingerprints, new_fingerprint];
        for (const labelDeltaElement of label_delta) {
            const color = colorGenerator.getColor(labelDeltaElement.new_label);
            if (labelDeltaElement.index >= colors.length) colors = [...colors, color];
            else colors[labelDeltaElement.index] = color;
        }
    }

    async function fetchAndDrawAll() {
        let vectors_query = await ApiRoutes.getFingerprints.fetch({params: {dataset, subset}})
        colors = [];
        for (let i = 0; i < vectors_query.length; i++) {
            vectors_query[i]["index"] = i;
            const color = colorGenerator.getColor(vectors_query[i].label);
            colors = [...colors, color];
        }
        fingerprints = [...vectors_query]
    }

    onMount(async () => {
        await fetchAndDrawAll();
    })

</script>

<div class="flex flex-col w-full md:w-1/2 mx-auto gap-5">
    <p class="self-center text-center text-xl font-bold">Long Signal Analysis</p>
    <p class="self-center text-right">{fingerprints.length} Fingerprints</p>
    <DataProviderStatus {dataProvider} bind:loading={loading}/>
    <ThreadsControl {dataset} {subset} handleReset={() => fetchAndDrawAll()} handleSingleItem={(data) => addNewItem(data)}/>
    <ClusterOverview {dataset} {subset} {fingerprints} {dataProvider} colorMapping={colorGenerator.getColorDictionary()}/>
    <!--    <ClusterDistribution {fingerprints} />-->
    <FingerprintLocations {dataset} {subset} {fingerprints} {colors} {dataProvider}/>
    <ProbabilitySculpting {dataset} {subset} {fingerprints}/>
</div>
