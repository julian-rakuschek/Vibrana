import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryFetch} from "lib/api/api";
import {Annotation} from "../types";

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

export const useLabels = (machine: string, sampleId: string): Annotation[] => {
  const data = useQueryFetch(ApiRoutes.getLabels, {params: {series: sampleId}});
  return data ?? [];
}

