import {writable} from 'svelte/store';
import {ColorMode, type ProjectedPoint, ProjectionMode, type ThreeChartsSettingsType, WindowMode} from "@lib/types";

export const defaultChartSettings: ThreeChartsSettingsType = {
    color: ColorMode.Radius,
    window: WindowMode.Sliding,
    windowSize: 1000,
    projection: ProjectionMode.Paths
}

export const filterRangePercent = writable<null | [number, number]>(null)
export const filterRangeIndexed = writable<null | [number, number]>(null)
export const chartSettings = writable<ThreeChartsSettingsType>(defaultChartSettings)
export const hoverPoint = writable<ProjectedPoint | undefined>(undefined)
export const hoverRange = writable<number[] | undefined>(undefined)
export const selectedProjectedPoints = writable<ProjectedPoint[]>([])
