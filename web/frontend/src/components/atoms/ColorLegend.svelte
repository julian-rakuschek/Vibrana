<script lang="ts">
    import {createColorsArray} from "@lib/helper/colorHelper";
    import {interpolateRdYlBu, interpolateTurbo} from "d3";
    import {ColorMode} from "@lib/types";

    export let colorMode: ColorMode;

    const radius_color_gradient = `linear-gradient(90deg, ${
        createColorsArray(20, {start: 0, end: 1, reverse: false, interpolateFunc: interpolateTurbo}).join(", ")
    })`;

    const distance_color_gradient = `linear-gradient(90deg, ${
        createColorsArray(20, {start: 0, end: 1, reverse: true, interpolateFunc: interpolateRdYlBu}).join(", ")
    })`;

    const explanation = (colorMode: ColorMode): string => {
        switch (colorMode) {
            case ColorMode.Frequency:
                return "Frequency is WIP";
            case ColorMode.Radius:
                return "Distance of each point to the center of the point cloud.";
            case ColorMode.Distance:
                return "Computed distance profile value based on the assigned labels.";
            default:
                return "";
        }
    };

</script>

<div class="flex flex-col w-full">
    <span class="text-sm text-gray-700 text-center">{explanation(colorMode)}</span>
    <div class="grid grid-cols-4 place-items-center">
        {#if colorMode === ColorMode.Radius}
            <span class="text-sm text-gray-700 col-span-1">Low Radius</span>
            <div class="w-full h-[10px] col-span-2" style={`background: ${radius_color_gradient}`}></div>
            <span class="text-sm text-gray-700 col-span-1">High Radius</span>
        {/if}

        {#if colorMode === ColorMode.Distance}
            <span class="text-sm text-gray-700 col-span-1">Low Similarity</span>
            <div class="w-full h-[10px] col-span-2" style={`background: ${distance_color_gradient}`}></div>
            <span class="text-sm text-gray-700 col-span-1">High Similarity</span>
        {/if}

        {#if colorMode === ColorMode.Frequency}
            <span class="text-sm text-gray-700 col-span-1"></span>
            <div class="w-full h-[10px] col-span-2" style={`background: black`}></div>
            <span class="text-sm text-gray-700 col-span-1"></span>
        {/if}
    </div>
</div>

