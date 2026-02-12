<script lang="ts">
    import {createColorsArray} from "@lib/helper/colorHelper";
    import {interpolateRdYlBu, interpolateTurbo, interpolateViridis} from "d3";
    import {ColorMode} from "@lib/types";

    interface Props {
        colorMode: ColorMode;
    }

    let { colorMode }: Props = $props();

    const radius_color_gradient = `linear-gradient(90deg, ${
        createColorsArray(20, {start: 0, end: 1, reverse: false, interpolateFunc: interpolateTurbo}).join(", ")
    })`;

    const distance_color_gradient = `linear-gradient(90deg, ${
        createColorsArray(20, {start: 0, end: 1, reverse: true, interpolateFunc: interpolateRdYlBu}).join(", ")
    })`;

    const freq_color_gradient = `linear-gradient(90deg, ${
        createColorsArray(20, {start: 0, end: 1, reverse: false, interpolateFunc: interpolateViridis}).join(", ")
    })`;

    const explanation = (colorMode: ColorMode): string => {
        switch (colorMode) {
            case ColorMode.Radius:
                return "Distance of each point to the center of the point cloud.";
            case ColorMode.Distance:
                return "The similarity of your marked labels with positions in the signal.";
            case ColorMode.Frequency:
                return "Mean amplitude of the SFFT over time."
            case ColorMode.Age:
                return "Age of the fingerprint."
            case ColorMode.Uncertainty:
                return "Uncertainty"
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
            <span class="text-sm text-gray-700 col-span-1">Low Amplitude</span>
            <div class="w-full h-[10px] col-span-2" style={`background: ${freq_color_gradient}`}></div>
            <span class="text-sm text-gray-700 col-span-1">High Amplitude</span>
        {/if}

        {#if colorMode === ColorMode.Age}
            <span class="text-sm text-gray-700 col-span-1">Old Fingerprint</span>
            <div class="w-full h-[10px] col-span-2" style={`background: ${freq_color_gradient}`}></div>
            <span class="text-sm text-gray-700 col-span-1">Recent Result</span>
        {/if}

        {#if colorMode === ColorMode.Uncertainty}
            <span class="text-sm text-gray-700 col-span-1">Certain</span>
            <div class="w-full h-[10px] col-span-2" style={`background: ${freq_color_gradient}`}></div>
            <span class="text-sm text-gray-700 col-span-1">Uncertain</span>
        {/if}
    </div>
</div>

