import {writable} from 'svelte/store';
import {type Color, ColorMode, type ThreeChartsSettingsType} from "@lib/types";
import {interpolateRdYlBu, interpolateTurbo} from "d3";
import {padArray} from "@lib/helper/util";

export const colorsTimeSeries = writable<Color[]>([]);
export const colorsProjection = writable<Color[]>([]);

export const computeRadiiNormalized = (projectedPoints: number[][]): number[] => {
    const radii = projectedPoints.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
    const max_rad = Math.max(...radii);
    return radii.map(r => r / max_rad);
}

const computeDistancesNormalized = (similarities: number[], normal_tube: [number, number]): number[] => {
    const shifted_min = (normal_tube[0] + normal_tube[1]) / 2
    const shifted_max = shifted_min + (normal_tube[1] - normal_tube[0])
    return similarities.map(s => (s - shifted_min) / (shifted_max - shifted_min))
}

const allBlack = (n: number): string[] => {
    return [...Array(n).keys()].map(() => "#000000");
}

export const computeColors = (settings: ThreeChartsSettingsType, projectedPoints: number[][], similarities: number[], normalTube: [number, number] | undefined, offset: number): void => {
    if (settings.color === ColorMode.Distance && normalTube !== undefined && similarities.length > 0) {
        const distanceValues = computeDistancesNormalized(similarities, normalTube);
        const colors = distanceValues.map((d): Color => ({color: interpolateRdYlBu(1 - d), value: d}))
        colorsTimeSeries.set(colors)
        colorsProjection.set(colors.slice(0, projectedPoints.length))
    } else if (settings.color === ColorMode.Radius) {
        const radiusValues = computeRadiiNormalized(projectedPoints);
        const paddedRadiusValues = padArray(radiusValues, offset)
        const projectedColors = radiusValues.map((r): Color => ({color: interpolateTurbo(r), value: r}))
        const timeSeriesColors = paddedRadiusValues.map((r): Color => ({color: interpolateTurbo(r), value: r}))
        colorsTimeSeries.set(timeSeriesColors)
        colorsProjection.set(projectedColors)
    } else if (settings.color === ColorMode.Frequency) {
        // Placeholder for Frequency
        colorsTimeSeries.set(allBlack(projectedPoints.length + offset).map((c): Color => ({color: c, value: 0})));
        colorsProjection.set(allBlack(projectedPoints.length).map((c): Color => ({color: c, value: 0})));
    } else {
        colorsTimeSeries.set(allBlack(projectedPoints.length + offset).map((c): Color => ({color: c, value: 0})));
        colorsProjection.set(allBlack(projectedPoints.length).map((c): Color => ({color: c, value: 0})));
    }
}