import {writable} from 'svelte/store';
import {ColorMode,
    type Config, type ProjectedPoint, ProjectionMode, type SelectedChunk, type ThreeChartsSettingsType, WindowMode} from "@lib/types";

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

export const displayMode = writable<string>("table")
export const simpleTable = writable<boolean>(false)
export const numberClusters = writable<number>(2)
export const selectedChunk = writable<SelectedChunk | undefined>(undefined)

export const fingerprintMode = writable<"tde" | "psd">("tde");