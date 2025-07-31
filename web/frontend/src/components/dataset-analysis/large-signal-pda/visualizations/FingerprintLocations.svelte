<script lang="ts">
    import type {Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import FingerprintRendering from "@components/atoms/FingerprintRendering.svelte";
    import CenteredLoadingSpinner from "@components/atoms/CenteredLoadingSpinner.svelte";
    import {deleteInterval, mergeIntervals} from "@lib/helper/util";
    import {ApiRoutes} from "@lib/api/ApiRoutes";

    enum MouseModes { ADD, DELETE }

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[] = [];
    export let colors: string[] = [];
    export let dataProvider: DataProvider;
    let loading = dataProvider.loading;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 100;
    let index_allocation: number[] = new Array(width).fill(-1);
    let currently_hovering = -1;
    let fingerprint_position = -1;
    let mouse_x = 0;
    let mouse_x_anchor = 0;
    let mouse_active = false;
    let mouse_mode: MouseModes = MouseModes.ADD;
    let intervals: [number, number][] = [];

    export function addFingerprint(vec: Fingerprint, color?: string) {
        if (!context) return;
        const start = Math.floor((vec.start_index / vec.max_index) * width);
        const rectangle_width = Math.floor((vec.slice_length / vec.max_index) * width);
        context.fillStyle = color ?? 'red';
        context.fillRect(start, 0, rectangle_width, height);
        for (let j = 0; j < rectangle_width; j++) {
            index_allocation[start + j] = vec.index;
        }
    }

    function visualizeSelectedIntervals() {
        if (!context) return;

        context.fillStyle = '#1a237e';
        context.globalAlpha = 0.3
        for (const interval of intervals) {
            context.fillRect(interval[0] * width, 0, (interval[1] - interval[0]) * width, height);
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

    export function render(fingerprints_to_draw: Fingerprint[], colors?: string[]) {
        if (!context) return;
        context.fillStyle = '#eeeeee';
        context.fillRect(0, 0, width, height);
        for (let i = 0; i < fingerprints_to_draw.length; i++) {
            addFingerprint(fingerprints_to_draw[i], colors && i < colors.length ? colors[i] : 'red');
        }
        visualizeSelectedIntervals()
    }

    function get_nearest_fingerprint(index: number) {
        if (index >= index_allocation.length || index < 0) return;
        let step = 0;
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

    async function saveIntervals() {
        await ApiRoutes.storeIntervals.fetch({ params: { dataset, subset }, data: intervals })
    }

    async function getIntervals() {
        intervals = await ApiRoutes.getIntervals.fetch({ params: { dataset, subset } })
    }

    function initMouse() {
        canvas.onmousemove = (e) => {
            mouse_x = e.clientX - canvas.getBoundingClientRect().left;
            get_nearest_fingerprint(Math.floor(mouse_x));
            render(fingerprints, colors);
        };
        canvas.onmousedown = (e) => {
            mouse_active = true;
            mouse_x_anchor = mouse_x;
            if (e.buttons === 1) mouse_mode = MouseModes.ADD;
            if (e.buttons === 2) mouse_mode = MouseModes.DELETE;
        };
        canvas.onmouseup = (e) => {
            const selected = [Math.min(mouse_x, mouse_x_anchor) / width, Math.max(mouse_x, mouse_x_anchor) / width];
            if (mouse_mode === MouseModes.ADD && mouse_active) {
                intervals.push(selected as [number, number])
                intervals = mergeIntervals(intervals);
            }
            if (mouse_mode === MouseModes.DELETE && mouse_active) {
                intervals = deleteInterval(intervals, selected as [number, number]);
            }
            mouse_active = false;
            saveIntervals();
        };
        canvas.oncontextmenu = function (e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    function resetMouse() {
        currently_hovering = -1
        mouse_active = false;

    }

    onMount(async () => {
        context = canvas.getContext('2d');
        initMouse();
        await getIntervals();
        render(fingerprints, colors);
    });

    $: {
        if (fingerprints.length === 0) index_allocation = new Array(width).fill(-1);
        render(fingerprints, colors);
    }
</script>

<div class="w-full" on:mouseleave={resetMouse}>
    <canvas class="noselect" {height} {width} bind:this={canvas}></canvas>
</div>
<div class="relative w-full" style={`width: ${width}px;`}>
    {#if currently_hovering !== -1}
        <div class="absolute bg-indigo-800 w-[50px] h-[50px] -translate-x-1/2 rotate-45"
             style={`left: ${fingerprint_position}px`}></div>
        <div class="absolute mt-3 p-3 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
             style={`left: ${fingerprint_position}px`}>
            {#if $loading}
                <CenteredLoadingSpinner/>
            {:else}
                <FingerprintRendering {dataProvider} fingerprint={fingerprints[currently_hovering]}/>
            {/if}
        </div>
    {/if}
</div>

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
