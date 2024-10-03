<script lang="ts">
    import NavigatorChart from "./NavigatorChart.svelte";
    import {ApiRoutes} from "../lib/api/ApiRoutes";
    import {onMount} from "svelte";
    import {
        ColorMode,
        type ProjectedPoint,
        ProjectionMode,
        type ThreeChartsSettingsType,
        WindowMode
    } from "../lib/types";
    import {padArray} from "../lib/helper/util";
    import {interpolateTurbo, interpolateRdYlBu} from "d3";
    import AnnotatorChart from "./AnnotatorChart.svelte";
    import ScatterPlot from "./ScatterPlot.svelte";
    import {filterRangeIndexed, filterRangePercent} from "../lib/stores";
    import ChartSettings from "./ChartSettings.svelte";

    let values: number[] = [];
    let projected: number[][] = [];
    let projectedIndexed: ProjectedPoint[] = [];
    let colors_ts: string[] = [];
    let colors_projected: string[] = [];
    let dataLoaded: boolean = false;
    let settings: ThreeChartsSettingsType = {
        color: ColorMode.Radius,
        window: WindowMode.Sliding,
        windowSize: 1000,
        projection: ProjectionMode.Paths
    }
    let hoverPoint: ProjectedPoint | undefined = undefined;
    let hoverRange: number[] | undefined = undefined;
    let selectedIndices: Set<ProjectedPoint> = new Set();
    let offset: number = 0;

    const compute_radius_norm = (data: number[][]): number[] => {
        const radii = data.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
        const max_rad = Math.max(...radii);
        return radii.map(r => r / max_rad);
    }

    const compute_radius_colors = (data: number[][]): string[] => {
        const radii = data.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
        const max_rad = Math.max(...radii);
        return radii.map(r => r / max_rad).map(r => interpolateTurbo(r));
    }

    const compute_distance_colors = (similarities: number[], normal_tube: [number, number]): string[] => {
        const shifted_min = (normal_tube[0] + normal_tube[1]) / 2
        const shifted_max = shifted_min + (normal_tube[1] - normal_tube[0])
        const normalized = similarities.map(s => (s - shifted_min) / (shifted_max - shifted_min))
        // const normalized = similarities.map(s => (s - normal_tube[0]) / (normal_tube[1] - normal_tube[0]))
        console.log(normalized)
        return normalized.map(n => interpolateRdYlBu(1 - n))
    }

    const all_black = (n: number): string[] => {
        return [...Array(n).keys()].map(i => "#000000");
    }

    export const compute_colors = (settings: ThreeChartsSettingsType, projected: number[][], similarities: number[], normal_tube: [number, number] | undefined, offset: number): {
        colors_ts: string[],
        colors_projected: string[]
    } => {
        if (settings.color === ColorMode.Distance && normal_tube !== undefined && similarities.length > 0) {
            const distance_colors = compute_distance_colors(similarities, normal_tube);

            return {colors_ts: distance_colors, colors_projected: distance_colors.slice(0, projected.length)}
        } else if (settings.color === ColorMode.Radius) {
            const radius_colors = compute_radius_colors(projected);
            const ts_radius_colors = padArray(radius_colors, offset)
            return {colors_ts: ts_radius_colors, colors_projected: radius_colors}
        } else if (settings.color === ColorMode.Frequency) {
            const all_black_ts = all_black(projected.length + offset);
            const all_black_pro = all_black(projected.length)
            return {colors_ts: all_black_ts, colors_projected: all_black_pro}
        } else {
            const all_black_ts = all_black(projected.length + offset);
            const all_black_pro = all_black(projected.length)
            return {colors_ts: all_black_ts, colors_projected: all_black_pro}
        }
    }

    const fetchData = async () => {
        try {
            values = await ApiRoutes.getSampleValues.fetch({
                params: {machine: "5-10-1t-10-16", sampleId: "abnormal-0003"}
            });
            projected = await ApiRoutes.getSampleProjected.fetch({
                params: {machine: "5-10-1t-10-16", sampleId: "abnormal-0003"}
            });
            const normalBand = await ApiRoutes.getNormalTube.fetch({
                params: {machineId: "5-10-1t-10-16"}
            });
            const similarities = await ApiRoutes.getSimilarities.fetch({
                params: {machineId: "5-10-1t-10-16", sampleId: "abnormal-0003"}
            });
            offset = values.length - projected.length
            projectedIndexed = projected.map((d, i): ProjectedPoint => ({
                projectedIndex: i,
                timeSeriesIndex: i + offset,
                coords: d
            }))
            colors_ts = compute_colors(settings, projected, similarities, normalBand, offset).colors_ts
            colors_projected = compute_colors(settings, projected, similarities, normalBand, offset).colors_projected
            dataLoaded = true;
        } catch (error) {
            console.error("Error fetching data", error);
        }
    };

    const reset = () => {
        filterRangeIndexed.set(null)
        filterRangePercent.set(null)
    }

    onMount(() => {
        fetchData()
    })
</script>

{#if dataLoaded}
    <button on:click={() => reset()}>Reset</button>
    <div class="fixed top-3 right-3 z-10">
        <ChartSettings bind:settings/>
    </div>
    <NavigatorChart radius_colors={compute_radius_norm(projected)} offset={offset} selectedIndices={selectedIndices}
                    values={values} colors={colors_ts} hoverPoint={hoverPoint}/>
    <AnnotatorChart selectedIndices={selectedIndices} values={values} colors={colors_ts} bind:hoverRange bind:hoverPoint
                    projectedIndexed={projectedIndexed} settings={settings}/>
    <ScatterPlot bind:selectedIndices bind:hoverRange values={values} settings={settings} projected={projected}
                 colors={colors_projected} projectedIndexed={projectedIndexed} bind:hoverPoint/>
{:else}
    <p>Loading chart data...</p>
{/if}
