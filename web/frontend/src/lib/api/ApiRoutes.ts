import {ApiRoute} from "./ApiRoute";
import type {AnalysisPostData, Annotation, AnomalyMetric, Dataset, DefaultAppResponse, Label, LabelBase, ParseStatus} from "../types";

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

export const dbRoutes = {
  getReadOnly: new ApiRoute<undefined, undefined, undefined, boolean>("GET", "/db/is_read_only"),
  getDatasetList: new ApiRoute<undefined, undefined, undefined, Dataset[]>("GET", "/db/datasets"),
  getChunks: new ApiRoute<undefined, {dataset: string; subset: string}, undefined, string[]>("GET", "/db/:dataset/:subset/chunks"),
  getChunkValues: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, undefined, number[]>("GET", "/db/:dataset/:subset/:chunk/values"),
  getChunkProjected: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, undefined, number[][]>("GET", "/db/:dataset/:subset/:chunk/projected"),
  getChunkEvents: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, undefined, number[]>("GET", "/db/:dataset/:subset/:chunk/events"),
  getChunkFreq: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, undefined, number[]>("GET", "/db/:dataset/:subset/:chunk/freq"),
  getLabels: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, undefined, Annotation[]>("GET", "/db/:dataset/:subset/:chunk/labels"),
  addLabel: new ApiRoute<LabelBase, {dataset: string; subset: string; chunk: string}, undefined, undefined>("POST", "/db/labels"),
  deleteLabelById: new ApiRoute<undefined, {labelId: string}, undefined, undefined>("DELETE", "/db/labels/byId/:labelId"),
  deleteLabelByPos: new ApiRoute<undefined, {dataset: string; subset: string; pos: string | number}, undefined, undefined>("DELETE", "/db/:dataset/:subset/:chunk/labels/:pos"),
  getNormals: new ApiRoute<undefined, { dataset: string; subset: string }, undefined, string[]>("GET", "/db/:dataset/:subset/normals"),
  addNormal: new ApiRoute<undefined, { dataset: string; subset: string; chunk: string }, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/:chunk/normals"),
  removeNormal: new ApiRoute<undefined, { dataset: string; subset: string; chunk: string }, undefined, DefaultAppResponse>("DELETE", "/db/:dataset/:subset/:chunk/normals"),
  reset: new ApiRoute<undefined, {dataset: string; subset: string}, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/reset"),
};

export const analysisRoutesDB = {
  getMDSEmbedding: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, {window_size: number}, number[][]>("GET", "/analysis/:dataset/:subset/:chunk/mdsEmbedding"),
  getSimilarities: new ApiRoute<undefined, {dataset: string; subset: string; chunk: string}, undefined, number[]>("GET", "/analysis/:dataset/:subset/:chunk/distanceProfile/quantized"),
  getNormalTube: new ApiRoute<undefined, {dataset: string; subset: string }, undefined, [number, number]>("GET", "/analysis/:dataset/:subset/normal_tube"),
  getAnomalyRatios: new ApiRoute<undefined, {dataset: string; subset: string}, undefined, AnomalyMetric[]>("GET", "/analysis/:dataset/:subset/anomaly_metrics"),
}

// RO = Read Only, this means the user needs to supply data that would normally be stored in the database
export const analysisRoutesRO = {
  getSimilaritiesRO: new ApiRoute<AnalysisPostData, {dataset: string; subset: string; chunk: string}, undefined, number[]>("POST", "/analysis/:dataset/:subset/:chunk/distanceProfile/quantized"),
  getNormalTubeRO: new ApiRoute<AnalysisPostData, {dataset: string; subset: string}, undefined, [number, number]>("POST", "/analysis/:dataset/:subset/normal_tube"),
  getAnomalyRatiosRO: new ApiRoute<AnalysisPostData, {dataset: string; subset: string}, undefined, AnomalyMetric[]>("POST", "/analysis/:dataset/:subset/anomaly_metrics"),
}

export const ApiRoutes = {
  ...dbRoutes,
  ...analysisRoutesDB,
  ...analysisRoutesRO
};