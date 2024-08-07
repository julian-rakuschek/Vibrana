import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryFetch} from "lib/api/api";
import {Annotation, Example} from "../types";

export const useDummyValues = (): number[] => {
  const data = useQueryFetch(ApiRoutes.getDummyValues);
  return data ?? [];
};

export const useDummyProjected = (): number[][] => {
  const data = useQueryFetch(ApiRoutes.getDummyProjected);
  return data ?? [];
};

export const useLabels = (series: string): Annotation[] => {
  const data = useQueryFetch(ApiRoutes.getLabels, {params: {series}});
  return data ?? [];
}