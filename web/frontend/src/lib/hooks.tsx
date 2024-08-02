import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryFetch} from "lib/api/api";
import {Example} from "../types";

export const useDummyValues = (): number[] => {
  const data = useQueryFetch(ApiRoutes.getDummyValues);
  return data ?? [];
};

export const useDummyProjected = (): number[][] => {
  const data = useQueryFetch(ApiRoutes.getDummyProjected);
  return data ?? [];
};