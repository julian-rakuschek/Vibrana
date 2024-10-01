<script lang="ts">
  import NavigatorChart from "./NavigatorChart.svelte";
  import {ApiRoutes} from "../lib/api/ApiRoutes";
  import {onMount} from "svelte";
  import {ColorMode, ProjectionMode, type ThreeChartsSettingsType, WindowMode} from "../lib/types";
  import {padArray} from "../lib/helper/util";
  import {interpolateTurbo, interpolateRdYlBu} from "d3";
  import AnnotatorChart from "./AnnotatorChart.svelte";
  import ScatterPlot from "./ScatterPlot.svelte";

  let count: number = 0
  const increment = () => {
    count += 1
  }


  let values: number[] = [];
  let projected: number[][] = [];
  let colors_ts: string[] = [];
  let dataLoaded: boolean = false;
  let settings = {color: ColorMode.Radius, window: WindowMode.Sliding, window_size: 1000, projection: ProjectionMode.Paths}

  let filterRangePercent: null | [number, number] = null;
  let filterRangeIndexed: null | [number, number] = null;

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

export const compute_colors = (settings: ThreeChartsSettingsType, projected: number[][], similarities: number[], normal_tube: [number, number] | undefined, offset: number): {colors_ts: string[], colors_projected: string[]} => {
    if (settings.color === ColorMode.Distance && normal_tube !== undefined && similarities.length > 0) {
        const distance_colors = compute_distance_colors(similarities, normal_tube);

        return {colors_ts: distance_colors, colors_projected: distance_colors.slice(0, projected.length)}
    }
    else if (settings.color === ColorMode.Radius) {
        const radius_colors = compute_radius_colors(projected);
        const ts_radius_colors = padArray(radius_colors, offset)
        return {colors_ts: ts_radius_colors, colors_projected: radius_colors}
    }
    else if (settings.color === ColorMode.Frequency) {
        const all_black_ts = all_black(projected.length + offset);
        const all_black_pro = all_black(projected.length)
        return {colors_ts: all_black_ts, colors_projected: all_black_pro}
    }
    else {
        const all_black_ts = all_black(projected.length + offset);
        const all_black_pro = all_black(projected.length)
        return {colors_ts: all_black_ts, colors_projected: all_black_pro}
    }
}

  const fetchData = async () => {
    try {
      values = await ApiRoutes.getSampleValues.fetch({
        params: { machine: "5-10-1t-10-16", sampleId: "abnormal-0003" }
      });
      projected = await ApiRoutes.getSampleProjected.fetch({
        params: { machine: "5-10-1t-10-16", sampleId: "abnormal-0003" }
      });
      const normalBand = await ApiRoutes.getNormalTube.fetch({
        params: { machineId: "5-10-1t-10-16" }
      });
      const similarities = await ApiRoutes.getSimilarities.fetch({
        params: { machineId: "5-10-1t-10-16", sampleId: "abnormal-0003" }
      });
      const offset = values.length - projected.length
      colors_ts = compute_colors(settings, projected, similarities, normalBand, offset).colors_ts
      dataLoaded = true;
    } catch (error) {
      console.error("Error fetching data", error);
    }
  };

  onMount(() => {
    fetchData()
  })
</script>

{#if dataLoaded}
  <NavigatorChart values={values} bind:filterRangePercent bind:filterRangeIndexed colors={colors_ts} />
  <AnnotatorChart values={values} filterRangeIndexed={filterRangeIndexed} colors={colors_ts} />
  <ScatterPlot projected={projected} colors={colors_ts} tsIndexOffset={values.length - projected.length} />
  <p>{filterRangePercent}</p>
{:else}
  <p>Loading chart data...</p>
{/if}
