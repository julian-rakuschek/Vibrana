<script lang="ts">
    import type {HyperplaneVector} from "@lib/types";
    import {onMount} from "svelte";
    import {DataProvider} from "@lib/dataProvider/dataProvider";
    import {interpolateTurbo} from "d3";


    export let dataProvider: DataProvider;
    export let hyperplane: HyperplaneVector | null;
    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null
    const size = 200;

    export function visualizeFingerprint(vec: HyperplaneVector) {
        const projected = dataProvider.get_fingerprint_data_javascript(vec);

        const min_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[0]
        const max_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[projected.length - 1]
        const min_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[0]
        const max_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[projected.length - 1]

        if (!context) return;
        context.fillStyle = "#FFFFFF";
        context.fillRect(0, 0, size, size);

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
        context = canvas.getContext('2d');
        if (hyperplane) visualizeFingerprint(hyperplane);
    })

    $: if (hyperplane) visualizeFingerprint(hyperplane);

</script>

<canvas height={size} width={size} bind:this={canvas}></canvas>
