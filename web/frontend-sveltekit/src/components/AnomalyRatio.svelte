<script lang="ts">
    import {interpolateRdYlBu, color} from "d3";
    import {colorIsDarkSimple} from "@lib/helper/util";
    export let anomalyRatio: number;
    const min_percentage = 0
    const max_percentage = 0.1
    $: anomalyRatioRounded = Math.round(anomalyRatio * 10000) / 100
    $: background_color = interpolateRdYlBu(1 - (anomalyRatioRounded - min_percentage) / (max_percentage - min_percentage))
    $: text_color = colorIsDarkSimple(color(background_color).hex()) ? '#FFFFFF' : '#000000';

</script>

<div style={`background-color: ${background_color}; color: ${text_color}`}
     class="w-[50px] flex flex-row justify-center items-center text-center rounded-lg p-0 h-[20px] text-xs">
    <span>{anomalyRatioRounded ?? ""}</span>
</div>