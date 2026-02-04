<script lang="ts">

    import {onMount} from "svelte";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {Play} from "svelte-hero-icons";
    import FancyButton from "@components/atoms/FancyButton.svelte";
    import {Pulse} from "svelte-loading-spinners";
    import type {ParameterSettingsUpdate} from "@lib/types";

    export let dataset: string;
    export let subset: string;
    export let fingerprintMode: "tde" | "psd";
    export let onRecomputeComplete: () => void;

    let eps: number;
    let minPoints: number;
    let sliding_window_size: number;
    let recomputing: boolean = false;

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

    $: loadInitialParameters(fingerprintMode)

</script>

<div class="grid grid-cols-2 gap-y-2">
    <p>Epsilon:</p>
    <input on:keyup={saveParameters} bind:value={eps} type="text"
           class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-20 rounded-lg">
    <p>Minimum Points:</p>
    <input on:keyup={saveParameters} bind:value={minPoints} type="text"
           class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-20 rounded-lg">
    {#if fingerprintMode === "tde"}
        <p>Sliding Window Size:</p>
    <input on:keyup={saveParameters} bind:value={sliding_window_size} type="text"
           class="bg-indigo-50 border-none py-0 px-2 border-indigo-800 h-[25px] w-20 rounded-lg">
    {/if}
</div>

{#if recomputing}
    <div class="bg-indigo-800 w-full rounded-lg flex flex-row gap-5 p-3 justify-center items-center">
        <Pulse color="#FFFFFF" size="30" unit="px" />
        <p class="text-white">Recomputing Clusters</p>
    </div>
{:else}
    <button class="h-7 w-full" on:click={async () => {await recomputeCluster();}}>
        <FancyButton button_color="primary" text="Recompute Clusters" text_size="text-md"/>
    </button>
{/if}
