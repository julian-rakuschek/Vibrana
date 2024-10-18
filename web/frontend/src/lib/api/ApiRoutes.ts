import {ApiRoute} from "./ApiRoute";
import type {AnalysisPostData, Annotation, AnomalyMetric, DefaultAppResponse, Label, LabelBase, ParseStatus} from "../types";

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

export const dbRoutes = {
  getReadOnly: new ApiRoute<undefined, undefined, undefined, boolean>("GET", "/db/is_read_only"),
  getMachinesList: new ApiRoute<undefined, undefined, undefined, string[]>("GET", "/db/machines"),
  getMachineSamples: new ApiRoute<undefined, {machineId: string}, undefined, string[]>("GET", "/db/:machineId/samples"),
  addMachine: new ApiRoute<{machineName: string}, undefined, undefined, DefaultAppResponse>("POST", "/db/machines/add"),
  getSampleValues: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/db/:machineId/samples/:sampleId/values"),
  getSampleProjected: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[][]>("GET", "/db/:machineId/samples/:sampleId/projected"),
  getSampleEvents: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/db/:machineId/samples/:sampleId/events"),
  getSampleFreq: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/db/:machineId/samples/:sampleId/freq"),
  getLabels: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, Annotation[]>("GET", "/db/labels/:machineId/:sampleId"),
  addLabel: new ApiRoute<LabelBase, {machineId: string; sampleId: string}, undefined, undefined>("POST", "/db/labels"),
  deleteLabelById: new ApiRoute<undefined, {labelId: string}, undefined, undefined>("DELETE", "/db/labels/byId/:labelId"),
  deleteLabelByPos: new ApiRoute<undefined, {machineId: string; sampleId: string; pos: string | number}, undefined, undefined>("DELETE", "/db/labels/:machineId/:sampleId/byPosition/:pos"),
  getNormals: new ApiRoute<undefined, { machineId: string }, undefined, string[]>("GET", "/db/normals/:machineId"),
  addNormal: new ApiRoute<undefined, { machineId: string, sampleId: string }, undefined, DefaultAppResponse>("POST", "/db/normals/:machineId/:sampleId"),
  removeNormal: new ApiRoute<undefined, { machineId: string, sampleId: string }, undefined, DefaultAppResponse>("DELETE", "/db/normals/:machineId/:sampleId"),
  reset: new ApiRoute<undefined, {machineId: string}, undefined, DefaultAppResponse>("POST", "/db/reset/:machineId"),
  getUploadStatus: new ApiRoute<undefined, {machineId: string; filename: string}, undefined, ParseStatus>("GET", "/db/:machineId/:filename/upload/status"),
};

export const analysisRoutesDB = {
  getMDSEmbedding: new ApiRoute<undefined, {machineId: string; sampleId: string}, {window_size: number}, number[][]>("GET", "/analysis/:machineId/:sampleId/mdsEmbedding"),
  getSimilarities: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, number[]>("GET", "/analysis/:machineId/:sampleId/distanceProfile/quantized"),
  getNormalTube: new ApiRoute<undefined, {machineId: string; }, undefined, [number, number]>("GET", "/analysis/:machineId/normal_tube"),
  getAnomalyRatios: new ApiRoute<undefined, {machineId: string;}, undefined, AnomalyMetric[]>("GET", "/analysis/:machineId/anomaly_metrics"),
}

// RO = Read Only, this means the user needs to supply data that would normally be stored in the database
export const analysisRoutesRO = {
  getSimilaritiesRO: new ApiRoute<AnalysisPostData, {machineId: string; sampleId: string}, undefined, number[]>("POST", "/analysis/:machineId/:sampleId/distanceProfile/quantized"),
  getNormalTubeRO: new ApiRoute<AnalysisPostData, {machineId: string; }, undefined, [number, number]>("POST", "/analysis/:machineId/normal_tube"),
  getAnomalyRatiosRO: new ApiRoute<AnalysisPostData, {machineId: string;}, undefined, AnomalyMetric[]>("POST", "/analysis/:machineId/anomaly_metrics"),
}

export const ApiRoutes = {
  ...dbRoutes,
  ...analysisRoutesDB,
  ...analysisRoutesRO
};