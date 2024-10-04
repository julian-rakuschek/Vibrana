import {ApiRoute} from "./ApiRoute";
import type {Annotation, AnomalyMetric, DefaultAppResponse, Label, LabelBase} from "../types";

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

export const dbRoutes = {
  getMachinesList: new ApiRoute<undefined, undefined, undefined, string[]>("GET", "/db/machines"),
  getMachineSamples: new ApiRoute<undefined, {machineId: string}, undefined, string[]>("GET", "/db/:machineId/samples"),
  getSampleValues: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/db/:machineId/samples/:sampleId/values"),
  getSampleProjected: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[][]>("GET", "/db/:machineId/samples/:sampleId/projected"),
  getSampleEvents: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/db/:machineId/samples/:sampleId/events"),
  getLabels: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, Annotation[]>("GET", "/db/labels/:machineId/:sampleId"),
  addLabel: new ApiRoute<LabelBase, {machineId: string; sampleId: string}, undefined, undefined>("POST", "/db/labels"),
  deleteLabelById: new ApiRoute<undefined, {labelId: string}, undefined, undefined>("DELETE", "/db/labels/byId/:labelId"),
  deleteLabelByPos: new ApiRoute<undefined, {pos: string | number}, undefined, undefined>("DELETE", "/db/labels/byPosition/:pos"),
  getNormals: new ApiRoute<undefined, { machineId: string }, undefined, string[]>("GET", "/db/normals/:machineId"),
  addNormal: new ApiRoute<undefined, { machineId: string, sampleId: string }, undefined, DefaultAppResponse>("POST", "/db/normals/:machineId/:sampleId"),
  removeNormal: new ApiRoute<undefined, { machineId: string, sampleId: string }, undefined, DefaultAppResponse>("DELETE", "/db/normals/:machineId/:sampleId"),
  reset: new ApiRoute<undefined, {machineId: string}, undefined, DefaultAppResponse>("POST", "/db/reset/:machineId"),
};

export const analysisRoutes = {
  getMDSEmbedding: new ApiRoute<undefined, {machineId: string; sampleId: string}, {window_size: number}, number[][]>("GET", "/analysis/:machineId/:sampleId/mdsEmbedding"),
  getSimilarities: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/analysis/:machineId/:sampleId/distanceProfile"),
  getNormalTube: new ApiRoute<undefined, {machineId: string; }, undefined, [number, number]>("GET", "/analysis/:machineId/normal_tube"),
  getAnomalyRatio: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, AnomalyMetric>("GET", "/analysis/:machineId/anomaly_metrics/:sampleId/"),
  getAnomalyRatios: new ApiRoute<undefined, {machineId: string;}, undefined, AnomalyMetric[]>("GET", "/analysis/:machineId/anomaly_metrics"),
}

export const ApiRoutes = {
  ...dbRoutes,
  ...analysisRoutes
};