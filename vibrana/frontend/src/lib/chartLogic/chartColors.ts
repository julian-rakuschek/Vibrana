import {writable} from 'svelte/store';
import {type ChartColors, type Color, ColorMode, type ThreeChartsSettingsType} from "@lib/types";
import {interpolateRdYlBu, interpolateTurbo, interpolateViridis} from "d3";
import {padArray} from "@lib/helper/util";

export const computeRadiiNormalized = (projectedPoints: number[][]): number[] => {
    const radii = projectedPoints.map(p => Math.sqrt(Math.pow(p[0], 2) + Math.pow(p[1], 2)));
    const min_rad = radii.toSorted((a, b) => a - b)[0]
    const max_rad = radii.toSorted((a, b) => a - b)[radii.length - 1]
    return radii.map(r => (r - min_rad) / (max_rad - min_rad));
}

const computeDistancesNormalized = (distances: number[], normal_tube: [number, number]): number[] => {
    const tolerance = 2
    const meanNormal = (normal_tube[0] + normal_tube[1]) / 2
    const tubeRadius = Math.abs(normal_tube[0] - normal_tube[1]) / 2
    const distancesToMeanNormal = distances.map(d => Math.abs(d - meanNormal))
    const maxDistanceFromMean = tubeRadius * tolerance
    return distancesToMeanNormal.map(s => s / maxDistanceFromMean)
}

const computeDistancesOutside = (distances: number[], normal_tube: [number, number]): number[] => {
    return distances.map(d => d < normal_tube[0] || d > normal_tube[1] ? 1 : 0)
}

const allBlack = (n: number): string[] => {
    return [...Array(n).keys()].map(() => "#000000");
}

export const computeColors = (colorMode: ColorMode, projectedPoints: number[][], similarities: number[], freq: number[], normalTube: [number, number] | undefined, offset: number): ChartColors => {
    if (colorMode === ColorMode.Distance && normalTube !== undefined && similarities.length > 0) {
        const distanceValues = computeDistancesNormalized(similarities, normalTube);
        const colors = distanceValues.map((d): Color => ({color: interpolateRdYlBu(1 - d), value: d}))
        return {tsColors: colors, projectedColors: colors.slice(0, projectedPoints.length)}
    } else if (colorMode === ColorMode.Radius) {
        const radiusValues = computeRadiiNormalized(projectedPoints);
        const paddedRadiusValues = padArray(radiusValues, offset)
        const projectedColors = radiusValues.map((r): Color => ({color: interpolateTurbo(r), value: r}))
        const timeSeriesColors = paddedRadiusValues.map((r): Color => ({color: interpolateTurbo(r), value: r}))
        return {tsColors: timeSeriesColors, projectedColors: projectedColors}
    } else if (colorMode === ColorMode.Frequency) {
        const colors = freq.map((d): Color => ({color: interpolateViridis(d), value: d}))
        return {tsColors: colors, projectedColors: colors.slice(0, projectedPoints.length)}
    } else {
        const colors = allBlack(projectedPoints.length + offset).map((c): Color => ({color: c, value: 0}))
        return {tsColors: colors, projectedColors: colors.slice(0, projectedPoints.length)}
    }
}

export type ColorInterpolateParams = {
  start: number;
  end: number;
  reverse: boolean;
  interpolateFunc: (t: number) => string;
};

// Src: https://medium.com/code-nebula/automatically-generate-chart-colors-with-chart-js-d3s-color-scales-f62e282b2b41
export function createColorsArray(dataLength: number, colorInterpolateParams: ColorInterpolateParams): string[] {
  const colorRange = colorInterpolateParams.end - colorInterpolateParams.start;
  const intervalSize = colorRange / dataLength;
  const colorArray = [];

  for(let i = 0; i < dataLength; i++) {
    const colorPoint: number = colorInterpolateParams.reverse ?
      (colorInterpolateParams.end - (i * intervalSize)) :
      (colorInterpolateParams.start + (i * intervalSize));
    colorArray.push(colorInterpolateParams.interpolateFunc(colorPoint));
  }

  return colorArray;
}