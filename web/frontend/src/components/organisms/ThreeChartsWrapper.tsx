import {ReactElement, useEffect, useState} from "react";
import {
    useClusteredProjection,
    useLabels, useNormalBand,
    useSampleEvents,
    useSampleProjected,
    useSampleValues,
    useSimilarities
} from "lib/hooks";
import ThreeCharts from "components/organisms/ThreeCharts";
import {ColorMode, ProjectionMode, ThreeChartsSettingsType} from "../../types";
import ThreeChartsOptimized from "components/organisms/ThreeChartsOptimized";
import {interpolateRdYlBu, interpolateTurbo} from "d3";
import {padArray} from "lib/util";

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

const compute_colors = (settings: ThreeChartsSettingsType, projected: number[][], similarities: number[], normal_tube: [number, number] | undefined, offset: number): {colors_ts: string[], colors_projected: string[]} => {
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

export default function ThreeChartsWrapper({machineId, sampleId, settings}: {
    machineId: string;
    sampleId: string;
    settings: ThreeChartsSettingsType
}): ReactElement {
    const timeseries = useSampleValues(machineId, sampleId);
    const projected = useSampleProjected(machineId, sampleId);
    const clustered = useClusteredProjection(machineId, sampleId, settings.window_size);
    const labels = useLabels(machineId, sampleId);
    const events = useSampleEvents(machineId, sampleId)
    const similarities = useSimilarities(machineId, sampleId);
    const normal_tube = useNormalBand(machineId);
    const [chartKey, setChartKey] = useState(0);
    const offset = timeseries.length - projected.length
    const colors = compute_colors(settings, projected, similarities, normal_tube, offset);

    useEffect(() => {
        setChartKey(chartKey + 1);
    }, [settings]);

    return <>
        {timeseries.length > 0 && projected.length > 0 && clustered.length > 0 &&
            <ThreeCharts
                key={chartKey}
                sampleId={sampleId} machineId={machineId} timeseries={timeseries}
                labels={labels}
                projected={settings.projection === ProjectionMode.Paths ? projected : clustered}
                settings={settings}
                events={events}
                colors_projected={colors.colors_projected}
                colors_ts={colors.colors_ts}
            />
        }
    </>
}