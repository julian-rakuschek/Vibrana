<script lang="ts">
    import type {HyperplaneVector} from "@lib/types";
    import {onMount} from "svelte";
    import { page } from '$app/stores';
    import {DataProvider} from "@lib/dataProvider/dataProvider";
    import {interpolateTurbo} from "d3";

    export let dataset: string;
    export let subset: string;
    export let hyperplane: HyperplaneVector;

    let dataProvider: DataProvider;
    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null
    const size = 200;

    export function vis(vectors: HyperplaneVector) {
        const res = dataProvider.get_fingerprint_data(vectors);
        console.log(res);
    }

    function testCanvas(projected: number[][]) {
        const min_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[0]
        const max_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[projected.length - 1]
        const min_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[0]
        const max_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[projected.length - 1]

        if (!context) return;
        context.fillStyle = "#000000";
        for (let i = 0; i < projected.length; i++) {
            const x = (projected[i][0] - min_x_value) / (max_x_value - min_x_value);
            const y = (projected[i][1] - min_y_value) / (max_y_value - min_y_value);
            const radius = Math.sqrt(Math.pow(x - 0.5, 2) + Math.pow(y - 0.5, 2)) * 2;
            const color = interpolateTurbo(radius);
            context.fillStyle = color;
            context.fillRect(x * size, y * size, 1, 1);
        }

    }

    onMount(async () => {
        context = canvas.getContext('2d')
        dataProvider = new DataProvider(
            dataset, subset,
            $page.data.config[dataset].subsets[subset].sliding_window_size,
            $page.data.config[dataset].in_memory
        )
        await dataProvider.wasm_load();
        const res = await dataProvider.get_fingerprint_data(hyperplane);
        testCanvas(res);
    })

</script>

<div>
    <canvas height={size} width={size} bind:this={canvas}></canvas>
</div>
