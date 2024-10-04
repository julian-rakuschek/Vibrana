<script lang="ts">
    import {Icon, CheckCircle} from "svelte-hero-icons";
    import AnomalyRatio from "@components/AnomalyRatio.svelte";

    export let machineId: string;
    export let sampleId: string;
    export let anomalyRatio: number | undefined;
    export let selected: boolean;
    export let selectModeActive: boolean;
</script>


<div class={`overflow-hidden group border-2 border-solid border-transparent ${selectModeActive ? "hover:border-green-600" : ""} relative flex flex-col justify-center items-center w-[400px] h-[150px] shadow-lg rounded-lg px-2 transition hover:shadow-xl`}>
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
    <div class="flex flex-row justify-between items-center w-full mb-3">
        <span>{sampleId}</span>
        {#if anomalyRatio !== undefined}
            <AnomalyRatio anomalyRatio={anomalyRatio}/>
        {/if}
    </div>
</div>
