<script lang="ts">

    import {onMount} from "svelte";

    enum MouseModes { ADD, DELETE }

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 100;
    let mouse_x = 0;
    let mouse_x_anchor = 0;
    let mouse_active = false;
    let mouse_mode: MouseModes = MouseModes.ADD;

    let intervals: [number, number][] = [];


    function mergeIntervals(intervals_to_merge: [number, number][]): [number, number][] {
        intervals_to_merge.sort((a, b) => a[0] - b[0]);
        const merged = [];

        for (const interval of intervals_to_merge) {
            if (!merged.length || interval[0] > merged[merged.length - 1][1]) {
                merged.push(interval);
            } else {
                merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], interval[1]);
            }
        }
        return merged;
    }

    function deleteInterval(intervals_to_delete_from: [number, number][], to_delete: [number, number]): [number, number][] {
        intervals_to_delete_from.sort((a, b) => a[0] - b[0]);
        let filtered_intervals: [number, number][] = [];

        for (const interval of intervals_to_delete_from) {
            if (interval[0] > to_delete[0] && interval[1] < to_delete[1]) continue;
            else if (interval[0] <= to_delete[0] && interval[1] <= to_delete[0]) filtered_intervals.push(interval);
            else if (interval[0] >= to_delete[1] && interval[1] >= to_delete[1]) filtered_intervals.push(interval);
            else if (interval[0] < to_delete[0] && interval[1] > to_delete[1]) {
                filtered_intervals.push([interval[0], to_delete[0]]);
                filtered_intervals.push([to_delete[1], interval[1]]);
            } else if (interval[0] < to_delete[0]) filtered_intervals.push([interval[0], to_delete[0]]);
            else if (interval[1] > to_delete[1]) filtered_intervals.push([to_delete[1], interval[1]]);


        }
        return filtered_intervals;
    }


    function render() {
        if (!context) return;
        context.fillStyle = '#eeeeee';
        context.fillRect(0, 0, width, height);


        context.fillStyle = '#1a237e';
        for (const interval of intervals) {
            context.fillRect(interval[0], 0, interval[1] - interval[0], height);
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

    function initMouse() {
        canvas.onmousemove = (e) => {
            mouse_x = e.clientX - canvas.getBoundingClientRect().left;
            render();
        };
        canvas.onmousedown = (e) => {
            mouse_active = true;
            mouse_x_anchor = mouse_x;
            if (e.buttons === 1) mouse_mode = MouseModes.ADD;
            if (e.buttons === 2) mouse_mode = MouseModes.DELETE;
        };
        canvas.onmouseup = (e) => {
            mouse_active = false;
            const selected = [Math.min(mouse_x, mouse_x_anchor), Math.max(mouse_x, mouse_x_anchor)];
            if (mouse_mode === MouseModes.ADD) {
                intervals.push(selected as [number, number])
                intervals = mergeIntervals(intervals);
            }
            if (mouse_mode === MouseModes.DELETE) {
                intervals = deleteInterval(intervals, selected as [number, number]);
            }

        };
        canvas.oncontextmenu = function (e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    onMount(() => {
        context = canvas.getContext('2d');
        render()
        initMouse()
    })
</script>

<div class="w-full p-10">
    <canvas {height} {width} bind:this={canvas} class="noselect"></canvas>
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