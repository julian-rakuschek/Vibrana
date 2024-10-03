import {ApiRoute} from "./ApiRoute";
import type { DefaultAppResponse, Label, LabelBase } from "../types";

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

export const dbRoutes = {
  getMachinesList: new ApiRoute<undefined, undefined, undefined, string[]>("GET", "/db/machines"),
  getMachineSamples: new ApiRoute<undefined, {machine: string}, undefined, string[]>("GET", "/db/:machine/samples"),
  getSampleValues: new ApiRoute<undefined, {machine: string; sampleId: string}, undefined, number[]>("GET", "/db/:machine/samples/:sampleId/values"),
  getSampleProjected: new ApiRoute<undefined, {machine: string; sampleId: string}, undefined, number[][]>("GET", "/db/:machine/samples/:sampleId/projected"),
  getSampleEvents: new ApiRoute<undefined, {machine: string; sampleId: string}, undefined, number[]>("GET", "/db/:machine/samples/:sampleId/events"),
  getLabels: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, Label[]>("GET", "/db/labels/:machineId/:sampleId"),
  addLabel: new ApiRoute<LabelBase, {machineId: string; sampleId: string}, undefined, undefined>("POST", "/db/labels"),
  deleteLabelById: new ApiRoute<undefined, {labelId: string}, undefined, undefined>("DELETE", "/db/labels/byId/:labelId"),
  deleteLabelByPos: new ApiRoute<undefined, {pos: string | number}, undefined, undefined>("DELETE", "/db/labels/byPosition/:pos"),
  getNormals: new ApiRoute<undefined, { machineId: string }, undefined, string[]>("GET", "/db/normals/:machineId"),
  addNormal: new ApiRoute<undefined, { machineId: string, sampleId: string }, undefined, DefaultAppResponse>("POST", "/db/normals/:machineId/:sampleId"),
  removeNormal: new ApiRoute<undefined, { machineId: string, sampleId: string }, undefined, DefaultAppResponse>("DELETE", "/db/normals/:machineId/:sampleId"),
  reset: new ApiRoute<undefined, {machine: string}, undefined, DefaultAppResponse>("POST", "/db/reset/:machine"),
};

export const analysisRoutes = {
  getMDSEmbedding: new ApiRoute<undefined, {machine: string; sampleId: string}, {window_size: number}, number[][]>("GET", "/analysis/:machine/:sampleId/clustering"),
  getSimilarities: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/analysis/:machineId/:sampleId/similarities"),
  getNormalTube: new ApiRoute<undefined, {machineId: string; }, undefined, [number, number]>("GET", "/analysis/:machineId/normal_band"),
  getAnomalyRatio: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number>("GET", "/analysis/:machineId/:sampleId/anomaly_ratio"),
  getAnomalyRatios: new ApiRoute<undefined, {machineId: string;}, undefined, [string, number][]>("GET", "/analysis/:machineId/anomaly_ratios"),
}

export const ApiRoutes = {
  ...dbRoutes,
  ...analysisRoutes
};