<script lang="ts">
    import * as d3 from "d3";
    import {interpolateRdYlBu} from "d3";

    export let distances: number[];
    export let normalTube: [number, number];

    let width = 300
    const height = 10

    const normalizeDistances = (distances: number[], normalTube: [number, number]) => {
        const tolerance = 2
        const meanNormal = (normalTube[0] + normalTube[1]) / 2
        const tubeRadius = Math.abs(normalTube[0] - normalTube[1]) / 2
        const distancesToMeanNormal = distances.map(d => Math.abs(d - meanNormal))
        const maxDistanceFromMean = tubeRadius * tolerance
        if (maxDistanceFromMean === 0 || isNaN(maxDistanceFromMean)) return distancesToMeanNormal.map(() => 1)
        return distancesToMeanNormal.map(s => s / maxDistanceFromMean).map(s => s > 1 ? 1 : s).map(s => 1 - s)
    }
    let distancesNormalized: number[];
    $: distancesNormalized = normalizeDistances(distances, normalTube);

    $: xScale = d3.scaleLinear().range([0, width]).domain([0, distances.length]);
    $: yScale = d3.scaleLinear().range([0, height]).domain([0, 1])

</script>
<div class="w-full" bind:clientWidth={width}>
    <svg width={width} height={height}>
        <g width={width} height={height}>
            {#each distancesNormalized as d, i}
                <rect
                        x={xScale(i)}
                        y={yScale(0)}
                        width={width / distances.length}
                        height={height}
                        opacity={1}
                        fill={interpolateRdYlBu(d)}
                />
            {/each}
        </g>
    </svg>
</div>