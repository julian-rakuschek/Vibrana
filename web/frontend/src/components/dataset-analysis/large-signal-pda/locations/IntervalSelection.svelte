<script lang="ts">
    import {onMount} from 'svelte';
    import {deleteInterval, mergeIntervals} from "@lib/helper/util";
    import {ApiRoutes} from "@lib/api/ApiRoutes";

    enum MouseModes { ADD, DELETE }

    export let dataset: string;
    export let subset: string;
    export let width = 1000;
    export let mouse_x = 0;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    const height = 100;
    let mouse_x_anchor = 0;
    let mouse_active = false;
    let mouse_mode: MouseModes = MouseModes.ADD;
    let intervals: [number, number][] = [];
    export let zoom_interval: [number, number] = [0, 1];

    function pixelToIntervalPosition(pixel: number) {
        const relative_pixel = pixel / width;
        return Math.abs(zoom_interval[0] - zoom_interval[1]) * relative_pixel + zoom_interval[0];
    }

    function visualizeSelectedIntervals() {
        if (!context) return;
        context.clearRect(0, 0, width, height);

        context.fillStyle = '#1a237e';
        context.globalAlpha = 0.3
        for (const interval of intervals) {
            const interval_start = (interval[0] - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
            const interval_end = (interval[1] - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
            context.fillRect(interval_start * width, 0, Math.abs(interval_start - interval_end) * width, height);
        }

        if (mouse_active) {
            context.fillStyle = mouse_mode === MouseModes.DELETE ? '#e53935' : '#4caf50';
            context.globalAlpha = 0.3
            const selected = [Math.min(mouse_x, mouse_x_anchor), Math.max(mouse_x, mouse_x_anchor)];
            context.fillRect(selected[0], 0, selected[1] - selected[0], height);
        }


        context.globalAlpha = 1
        if (mouse_mode === MouseModes.DELETE) context.fillStyle = '#e53935';
        if (mouse_mode === MouseModes.ADD) context.fillStyle = '#4caf50';
        if (!mouse_active) context.fillStyle = '#1a237e';
        context.fillRect(mouse_x, 0, 1, height);
    }

    async function saveIntervals() {
        await ApiRoutes.storeIntervals.fetch({ params: { dataset, subset }, data: intervals })
    }

    export async function resetIntervals() {
        intervals = [];
        await ApiRoutes.storeIntervals.fetch({ params: { dataset, subset }, data: [] })
        visualizeSelectedIntervals();
    }

    function zoomIntensity(interval_width: number) {
        return 0.01 * Math.pow(10, interval_width);
    }

    function zoomIn(mouse_x: number) {
        const split = mouse_x / width;
        const current_width = Math.abs(zoom_interval[1] - zoom_interval[0]);
        const intensity = zoomIntensity(current_width);

        const new_start = zoom_interval[0] + split * intensity;
        const new_end = zoom_interval[1] - (1 - split) * intensity;
        const new_width = Math.abs(new_end - new_start);

        if (new_width < 0.005) return;
        zoom_interval = [new_start, new_end];
    }


    function zoomOut(mouse_x: number) {
        const split = mouse_x / width;
        const current_width = Math.abs(zoom_interval[0] - zoom_interval[1])
        zoom_interval = [
            Math.max(0, zoom_interval[0] - (1 - split) * zoomIntensity(current_width)),
            Math.min(1, zoom_interval[1] + split * zoomIntensity(current_width))
        ]
    }

    async function getIntervals() {
        intervals = await ApiRoutes.getIntervals.fetch({ params: { dataset, subset } })
    }

    function initMouse() {
        canvas.onmousemove = (e) => {
            mouse_x = e.clientX - canvas.getBoundingClientRect().left;
            if (!mouse_active) mouse_x_anchor = mouse_x;
            visualizeSelectedIntervals();
        };
        canvas.onmousedown = (e) => {
            mouse_active = true;
            mouse_x_anchor = mouse_x;
            if (e.buttons === 1) mouse_mode = MouseModes.ADD;
            if (e.buttons === 2) mouse_mode = MouseModes.DELETE;
        };
        canvas.onmouseup = (e) => {
            mouse_active = false;
            const selected = [
                Math.min(pixelToIntervalPosition(mouse_x), pixelToIntervalPosition(mouse_x_anchor)),
                Math.max(pixelToIntervalPosition(mouse_x), pixelToIntervalPosition(mouse_x_anchor))
            ];
            if (mouse_mode === MouseModes.ADD) {
                intervals.push(selected as [number, number])
                intervals = mergeIntervals(intervals);
            }
            if (mouse_mode === MouseModes.DELETE) {
                intervals = deleteInterval(intervals, selected as [number, number]);
            }
            saveIntervals();
        };
        canvas.onwheel = (e) => {
            if (e.deltaY < 0) {
                zoomIn(mouse_x)
            } else {
                zoomOut(mouse_x)
            }
            visualizeSelectedIntervals();
        }
        canvas.oncontextmenu = function (e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    function resetMouse() {
        mouse_active = false;
        mouse_x = -1;
    }

    onMount(async () => {
        context = canvas.getContext('2d');
        initMouse();
        await getIntervals();
        visualizeSelectedIntervals();
    });

</script>

<canvas on:mouseleave={resetMouse} class="noselect" {height} {width} bind:this={canvas}></canvas>

<style>
    .noselect {
        -webkit-touch-callout: none !important;
        -webkit-user-select: none !important;
        -webkit-user-drag: none !important;
        -khtml-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
</style>