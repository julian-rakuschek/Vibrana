<script lang="ts">
    import FancyButton from '@components/atoms/FancyButton.svelte';
    import {Pause, Play, Trash} from 'svelte-hero-icons';
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {onMount} from 'svelte';
    import type {ClusterDelta, Fingerprint, ParameterSettingsUpdate} from '@lib/types';

    interface Props {
        dataset: string;
        subset: string;
        running?: boolean;
        handleReset: () => void;
        handleSingleItem: (new_fingerprint: Fingerprint, label_delta: ClusterDelta) => void;
    }

    let {
        dataset,
        subset,
        running = $bindable(false),
        handleReset,
        handleSingleItem
    }: Props = $props();

    let slice_size: number = $state(0);
    let sampling_strategy: string = $state("random");

    async function saveParameters() {
        await ApiRoutes.storeParameters.fetch({
            params: {dataset, subset},
            data: {sampling: {slice_size: Number.parseFloat(slice_size), samplingAlgorithm: sampling_strategy}}
        })
    }

    async function activateComputing() {
        await ApiRoutes.activateComputing.fetch({params: {dataset, subset}});
        running = true;
    }

    async function pauseComputing() {
        await ApiRoutes.pauseComputing.fetch({params: {dataset, subset}});
        running = false;
    }

    async function getComputingStatus(): Promise<boolean> {
        return await ApiRoutes.computingStatus.fetch({params: {dataset, subset}});
    }

    async function oneStep() {
        const data = await ApiRoutes.computeSingleStep.fetch({params: {dataset, subset}});
        if (handleSingleItem) handleSingleItem(data.new_fingerprint, data.labels);
    }

    async function clearVectors() {
        await ApiRoutes.clearFingerprints.fetch({params: {dataset, subset}});
        if (handleReset) handleReset();
    }

    async function loadInitialSliceSize() {
        const params = await ApiRoutes.getParameters.fetch({params: {dataset, subset}})
        slice_size = params.sampling.slice_size
        sampling_strategy = params.sampling.samplingAlgorithm
    }

    onMount(async () => {
        running = await getComputingStatus();
        await loadInitialSliceSize()
    });
</script>

<div class="flex flex-row w-full gap-2 items-center justify-center">
    <button class="h-10 w-10" onclick={async () => {await pauseComputing(); await clearVectors()}}>
        <FancyButton icon="{Trash}" button_color="danger"/>
    </button>
    <button class="h-10" onclick={async () => {await pauseComputing(); await oneStep()}}>
        <FancyButton button_color="primary" text="Single Step"/>
    </button>
    <button class="h-10 w-10" onclick={async () => {await pauseComputing();}}>
        <FancyButton icon="{Pause}" button_color="primary"/>
    </button>

    <button class="h-10 w-10" onclick={async () => {await activateComputing();}}>
        <FancyButton icon="{Play}" button_color="primary"/>
    </button>
</div>
<div class="grid grid-cols-2 gap-y-2 mt-4">
    <p>Slice Size:</p>
    <input onkeyup={saveParameters} bind:value={slice_size} type="text"
           class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-full rounded-lg">
    <p>Sampling:</p>
    <select onchange={saveParameters} bind:value={sampling_strategy} name="sampling" id="sampling" class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-full rounded-lg">
        <option value="random">Random</option>
        <option value="binary">Binary Search</option>
        <option value="gaps">Gap Filling</option>
        <option value="linear">Linear</option>
    </select>
</div>