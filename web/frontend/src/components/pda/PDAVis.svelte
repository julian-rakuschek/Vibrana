<script lang="ts">
    import type {HyperplaneVector} from "@lib/types";
    import {onMount} from "svelte";
    import {DataProvider} from "@lib/dataProvider/dataProvider";
    import {page} from '$app/stores';
    import FingerprintVis from "@components/pda/FingerprintVis.svelte";
    import PDAAging from "@components/pda/PDAAging.svelte";

    export let vectors: HyperplaneVector[] = []
    export let colors: string[] = []
    export let dataset: string;
    export let subset: string;

    console.log(vectors)

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null
    const width = 1000;
    const height = 100;
    const index_allocation: number[] = new Array(width).fill(-1);
    let currently_hovering = -1;
    let fingerprint_position = -1;
    let dataProvider: DataProvider;

    export function addVector(vec: HyperplaneVector, color?: string) {
        if (!context) return;
        const start = Math.floor((vec.start_index / vec.max_index) * width);
        const rectangle_width = Math.floor((vec.slice_length / vec.max_index) * width);
        context.fillStyle = color ?? "red"
        context.fillRect(start, 0, rectangle_width, height)
        for (let j = 0; j < rectangle_width; j++) index_allocation[start + j] = vec.index;
    }

    export function drawVectors(vectors_to_draw: HyperplaneVector[], colors?: string[]) {
        if (!context) return;
        context.fillStyle = "#eeeeee"
        context.fillRect(0, 0, width, height)
        for (let i = 0; i < vectors_to_draw.length; i++) {
            addVector(vectors_to_draw[i], colors && i < colors.length ? colors[i] : "red");
        }
    }

    onMount(async () => {
        context = canvas.getContext('2d')
        dataProvider = new DataProvider(
            dataset, subset,
            $page.data.config[dataset].subsets[subset].sliding_window_size,
            $page.data.config[dataset].in_memory
        )
        await dataProvider.load();
        canvas.onmousemove = (e) => {
            const r = canvas.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
            const index = Math.floor(x)
            if (index >= index_allocation.length || index < 0) return;
            let step = 0
            currently_hovering = -1;
            fingerprint_position = -1;
            while (step < index_allocation.length) {
                const left = index - step >= 0 ? index - step : 0;
                const right = index + step < index_allocation.length ? index + step : index_allocation.length - 1;
                if (index_allocation[left] !== -1) {
                    currently_hovering = index_allocation[left];
                    fingerprint_position = left;
                    break;
                }
                if (index_allocation[right] !== -1) {
                    currently_hovering = index_allocation[right];
                    fingerprint_position = right;
                    break;
                }
                step++;
            }
        }
        drawVectors(vectors, colors);
    })
</script>

<div class="flex flex-col items-center justify-center">
    <div>
        <canvas height={height} width={width} bind:this={canvas}></canvas>
    </div>
    <div class="relative w-full h-[200px]" style={`width: ${width}px;`}>
        {#if currently_hovering !== -1}
            <div class="absolute bg-indigo-800 w-[50px] h-[50px] -translate-x-1/2 rotate-45"
                 style={`left: ${fingerprint_position}px`}></div>
            <div class="absolute mt-3 p-3 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
                 style={`left: ${fingerprint_position}px`}>
                <FingerprintVis dataProvider={dataProvider} hyperplane={vectors[currently_hovering]}/>
            </div>
        {/if}
    </div>
    <div>
        <PDAAging aging={index_allocation} />
    </div>
</div>

