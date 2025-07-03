<script lang="ts">
    import type {HyperplaneVector} from "@lib/types";
    import {onMount} from "svelte";

    export let vectors: HyperplaneVector[] = []

    console.log(vectors)

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null

    onMount(() => {
		context = canvas.getContext('2d')
        if (context) {
            context.fillStyle = "#eeeeee"
            context.fillRect(0, 0, 1000, 100)
            for (const vec of vectors) {
                context.fillStyle = "red"
                context.fillRect((vec.start_index / vec.max_index) * 1000, 0, (vec.slice_length / vec.max_index) * 1000, 100)
            }
        }
	})
</script>

<canvas height="100" width="1000" bind:this={canvas}></canvas>