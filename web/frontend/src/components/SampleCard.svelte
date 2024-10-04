<script lang="ts">
    import {Icon, CheckCircle} from "svelte-hero-icons";
    import AnomalyRatio from "@components/AnomalyRatio.svelte";
    import type {AnomalyMetric} from "@lib/types";
    import DistanceIndicator from "@components/DistanceIndicator.svelte";

    export let machineId: string;
    export let sampleId: string;
    export let anomaly: AnomalyMetric | undefined;
    export let normalTube: [number, number]
    export let selected: boolean;
    export let selectModeActive: boolean;

    let width;

</script>


<div bind:clientWidth={width} class={`overflow-hidden group border-2 border-solid border-transparent ${selectModeActive ? "hover:border-green-600" : ""} relative flex flex-col justify-center items-center w-[400px] h-[170px] shadow-lg rounded-lg px-2 transition hover:shadow-xl`}>
    {#if selectModeActive && selected }
        <div class="absolute top-1 left-1 hidden group-hover:block px-2 py-1">
            <Icon src="{CheckCircle}" class="w-5 h-5 text-green-600"/>
        </div>
    {/if}
    {#if selected }
        <div class="absolute top-1 left-1 flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
            <Icon src="{CheckCircle}" solid class="w-4 h-4 text-white"/>
            Anomaly-Free
        </div>
    {/if}
    <img src={`/api/db/${machineId}/samples/${sampleId}/thumbnail`} alt="thumbnail"/>
    {#if anomaly !== undefined}
        <div class="w-full h-[10px] flex justify-center">
            <DistanceIndicator distances={anomaly.distances_reduced} normalTube={normalTube} width={Math.floor(width * 0.95)} height={10} />
        </div>
    {/if}
    <div class="flex flex-row justify-center items-center w-full gap-3 mb-3 mt-3">
        <span class="leading-none">{sampleId}</span>
        {#if anomaly !== undefined}
            <AnomalyRatio anomalyRatio={anomaly.ratio}/>
        {/if}
    </div>
</div>
