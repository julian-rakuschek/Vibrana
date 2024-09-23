import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryFetch} from "lib/api/api";
import {Annotation, Label} from "../types";

export const useMachines = (): string[] => {
  const data = useQueryFetch(ApiRoutes.getMachinesList);
  return data ?? [];
}

export const useSamples = (machine: string): string[] => {
  const data = useQueryFetch(ApiRoutes.getMachineSamples, {params: {machine}});
  return data ?? [];
}

export const useSampleValues = (machine: string, sampleId: string): number[] => {
  const data = useQueryFetch(ApiRoutes.getSampleValues, {params: {machine, sampleId}});
  return data ?? [];
}

export const useSampleProjected = (machine: string, sampleId: string): number[][] => {
  const data = useQueryFetch(ApiRoutes.getSampleProjected, {params: {machine, sampleId}});
  return data ?? [];
};

export const useSampleEvents = (machine: string, sampleId: string): number[] => {
  const data = useQueryFetch(ApiRoutes.getSampleEvents, {params: {machine, sampleId}});
  return data ?? [];
};

export const useClusteredProjection = (machine: string, sampleId: string, window_size: number): number[][] => {
  const data = useQueryFetch(ApiRoutes.getMDSEmbedding, {params: {machine, sampleId}, queryParams: {window_size}});
  return data ?? [];
}

export const useLabels = (machineId: string, sampleId: string): Label[] => {
  const data = useQueryFetch(ApiRoutes.getLabels, {params: {sampleId, machineId}});
  return data ?? [];
}

export const useNormals = (machineId: string): string[] => {
  const data = useQueryFetch(ApiRoutes.getNormals, {params: {machineId}});
  return data ?? [];
}

export const useSimilarities = (machineId: string, sampleId: string): number[] => {
  const data = useQueryFetch(ApiRoutes.getSimilarities, {params: {machineId, sampleId}});
  return data ?? [];
}

export const useNormalBand = (machineId: string): [number, number] | undefined => {
  return useQueryFetch(ApiRoutes.getNormalTube, {params: {machineId}});
}

export const useAnomalyScore = (machineId: string, sampleId: string): number | undefined => {
  return useQueryFetch(ApiRoutes.getAnomalyRatio, {params: {machineId, sampleId}});
}

export const useAnomalyScores = (machineId: string): [string, number][] | undefined => {
  return useQueryFetch(ApiRoutes.getAnomalyRatios, {params: {machineId}});
}