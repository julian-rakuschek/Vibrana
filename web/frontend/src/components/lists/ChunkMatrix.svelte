<script lang="ts">
    import type {AnomalyMetric, LabelCount} from "@lib/types";

    export let dataset: string;
    export let subset: string;
    export let chunks: string[];
    export let normals: string[];
    export let anomaly_ratios: AnomalyMetric[];
    export let normalTube: [number, number];
    export let labelCounts: LabelCount[];

    let selected_chunk: string | undefined = undefined;


    const get_anomaly = (needle: string, anomaly_ratios: AnomalyMetric[]): AnomalyMetric | undefined => {
        const res = anomaly_ratios.find(a => a.chunk == needle)
        if (res) return res;
        else return undefined;
    }
</script>

<div class="grid grid-cols-2 place-items-start">
    <div class="flex flex-row flex-wrap mt-5">
        {#each chunks as chunk}
            <button class={`flex flex-col border-4 ${chunk === selected_chunk ? "border-indigo-500" : "border-transparent"}`} on:click={() => selected_chunk = chunk}>
                <img src={`/api/db/${dataset}/${subset}/${chunk}/projected_thumbnail`} alt="thumbnail" class=" object-scale-down h-20"/>
            </button>
        {/each}
    </div>
    {#if selected_chunk}
        <div class="flex flex-col justify-center">
            <div class="w-full grid place-items-center">
                <a class="text-center text-xl font-semibold text-indigo-600 border-dotted border-b-2 border-b-indigo-600 hover:text-indigo-800 hover:border-indigo-800" href={`/datasets/${dataset}/${subset}/${selected_chunk}`}>{selected_chunk}</a>
            </div>
            <img src={`/api/db/${dataset}/${subset}/${selected_chunk}/thumbnail`} alt="thumbnail" class=" object-scale-down w-full"/>
            <img src={`/api/db/${dataset}/${subset}/${selected_chunk}/spectrogram`} alt="thumbnail" class=" object-scale-down w-full"/>
            <img src={`/api/db/${dataset}/${subset}/${selected_chunk}/projected_thumbnail`} alt="thumbnail" class=" object-scale-down w-full"/>
        </div>
    {/if}
</div>
