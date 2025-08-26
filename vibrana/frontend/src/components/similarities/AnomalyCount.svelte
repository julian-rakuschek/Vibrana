<script lang="ts">
    import {interpolateRdYlBu, color} from "d3";
    import {colorIsDarkSimple} from "@lib/helper/util";
    export let anomalyCount: number;
    const min_ratio = 0
    const max_ratio = 10
    $: background_color = interpolateRdYlBu(1 - (anomalyCount - min_ratio) / (max_ratio - min_ratio))
    $: text_color = colorIsDarkSimple(color(background_color).hex()) ? '#FFFFFF' : '#000000';

</script>

<div style={`background-color: ${background_color}; color: ${text_color}`}
     class="w-[50px] flex flex-row justify-center items-center text-center rounded-lg p-0 h-[20px] text-xs">
    <span>{anomalyCount ?? ""}</span>
</div>