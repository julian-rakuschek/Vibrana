<script lang="ts">
    import {formatUnixTimestamp} from "@lib/helper/util";
    interface Props {
        width: number;
        mouse_x: number;
        timestamps?: number[];
    }

    let { width, mouse_x, timestamps = [] }: Props = $props();
</script>

<div class="relative w-full" style={`width: ${width}px;`}>
    {#if mouse_x !== -1}
        <div class="absolute bg-indigo-800 w-[20px] h-[20px] top-6 -translate-x-1/2 rotate-45"
             style={`left: ${mouse_x}px`}></div>
        <div class="absolute -top-4 p-1.5 bg-white rounded-xl shadow-xl -translate-x-1/2 border-2 border-solid border-indigo-800"
             style={`left: ${mouse_x}px`}>
            {#if Math.floor(mouse_x) < timestamps.length}
                <p class="text-center text-xs">{formatUnixTimestamp(timestamps[Math.floor(mouse_x)]).isoDate}</p>
                <p class="text-center text-sm">{formatUnixTimestamp(timestamps[Math.floor(mouse_x)]).time}</p>
            {/if}
        </div>
    {/if}
</div>