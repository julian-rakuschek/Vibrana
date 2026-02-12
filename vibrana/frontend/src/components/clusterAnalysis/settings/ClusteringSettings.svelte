<script lang="ts">
    import {onMount} from "svelte";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import FancyButton from "@components/atoms/FancyButton.svelte";
    import {Pulse} from "svelte-loading-spinners";
    import type {ParameterSettingsUpdate} from "@lib/types";
    import Tooltip from "@components/atoms/Tooltip.svelte";

    interface Props {
        dataset: string;
        subset: string;
        fingerprintMode: "tde" | "psd";
        onRecomputeComplete: () => void;
    }

    let {
        dataset,
        subset,
        fingerprintMode,
        onRecomputeComplete
    }: Props = $props();

    let eps: number = $state();
    let minPoints: number = $state();
    let sliding_window_size: number = $state();
    let recomputing: boolean = $state(false);

    async function saveParameters() {
        const payload: ParameterSettingsUpdate = {
            [fingerprintMode]: {
                eps: Number.parseFloat(eps),
                minPoints: Number.parseFloat(minPoints)
            }
        }
        if (fingerprintMode === "tde") {
            payload.tde!.sliding_window_size = Number.parseFloat(sliding_window_size);
        }

        await ApiRoutes.storeParameters.fetch({
            params: {dataset, subset},
            data: payload
        })
    }

    async function recomputeCluster() {
        recomputing = true;
        await ApiRoutes.recomputeClusters.fetch({params: {dataset, subset}})
        recomputing = false;
        onRecomputeComplete();
    }

    async function loadInitialParameters(fingerprintMode: "tde" | "psd") {
        const params = await ApiRoutes.getParameters.fetch({params: {dataset, subset}})
        eps = params[fingerprintMode].eps;
        minPoints = params[fingerprintMode].minPoints;
        if (fingerprintMode === "tde") sliding_window_size = params[fingerprintMode].sliding_window_size;
    }

    onMount(async () => {
        loadInitialParameters(fingerprintMode)
    })

    $effect(() => {
        loadInitialParameters(fingerprintMode)
    });

</script>

<div class="grid grid-cols-2 gap-y-2">
    <p>Epsilon:</p>
    <div class="flex flex-row items-center gap-1">
        <input onkeyup={saveParameters} bind:value={eps} type="text"
               class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-20 rounded-lg">
        <Tooltip color="#303f9f"
                 text="Controls the sensitivity of the clustering algorithm. Higher epsilon means less clusters while lower epsilon results in more clusters."/>
    </div>
    <p>Minimum Points:</p>
    <div class="flex flex-row items-center gap-1">
        <input onkeyup={saveParameters} bind:value={minPoints} type="text"
               class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-20 rounded-lg">
        <Tooltip color="#303f9f" text="The minimum number of points required for a cluster to form."/>
    </div>
    {#if fingerprintMode === "tde"}
        <p>Sliding Window Size:</p>
        <div class="flex flex-row items-center gap-1">
        <input onkeyup={saveParameters} bind:value={sliding_window_size} type="text"
               class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-20 rounded-lg">
            <Tooltip color="#303f9f" text="The number of points used to compute the projection-based fingerprint. A larger window size can capture lower frequencies."/>
        </div>
    {/if}
</div>

{#if recomputing}
    <div class="bg-indigo-800 w-full rounded-lg flex flex-row gap-5 p-3 justify-center items-center">
        <Pulse color="#FFFFFF" size="30" unit="px"/>
        <p class="text-white">Recomputing Clusters</p>
    </div>
{:else}
    <button class="h-7 w-full" onclick={async () => {await recomputeCluster();}}>
        <FancyButton button_color="primary" text="Recompute Clusters" text_size="text-md"/>
    </button>
{/if}
