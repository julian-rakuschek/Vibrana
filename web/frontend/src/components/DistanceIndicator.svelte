<script lang="ts">
    import {onMount} from "svelte";
    import * as d3 from "d3";
    import {interpolateRdYlBu} from "d3";

    export let distances: number[];
    export let normalTube: [number, number];

    export let width = 300
    export let height = 10

    const normalizeDistances = () => {
        const tolerance = 2
        const meanNormal = (normalTube[0] + normalTube[1]) / 2
        const tubeRadius = Math.abs(normalTube[0] - normalTube[1]) / 2
        const distancesToMeanNormal = distances.map(d => Math.abs(d - meanNormal))
        const maxDistanceFromMean = tubeRadius * tolerance
        return distancesToMeanNormal.map(s => s / maxDistanceFromMean).map(s => s > 1 ? 1 : s).map(s => 1 - s)
    }
    let distancesNormalized: number[] = normalizeDistances();
    console.log(distancesNormalized)

    const xScale = d3
        .scaleLinear()
        .range([0, width])
        .domain([0, distances.length]);

    const yScale = d3
        .scaleLinear()
        .range([0, height])
        .domain([0, 1])

    const rect_width = width / distances.length;
    const rect_height = height;

    onMount(() => {

    });
</script>

<svg width={width} height={height}>
    <g width={width} height={height}>
        {#each distancesNormalized as d, i}
            <rect
                    x={xScale(i)}
                    y={yScale(0)}
                    width={rect_width}
                    height={rect_height}
                    opacity={1}
                    fill={interpolateRdYlBu(d)}
            />
        {/each}
    </g>
</svg>