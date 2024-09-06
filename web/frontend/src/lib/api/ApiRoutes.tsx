import {ApiRoute} from "lib/api/ApiRoute";
import {Annotation, Label, LabelBase} from "../../types";

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
  getLabels: new ApiRoute<undefined, {machineId: string; sampleId: string}, undefined, Label[]>("GET", "/db/labels/:machineId/:sampleId"),
  addLabel: new ApiRoute<LabelBase, {machineId: string; sampleId: string}, undefined, undefined>("POST", "/db/labels"),
  deleteLabelById: new ApiRoute<undefined, {labelId: string}, undefined, undefined>("DELETE", "/db/labels/byId/:labelId"),
  deleteLabelByPos: new ApiRoute<undefined, {pos: string | number}, undefined, undefined>("DELETE", "/db/labels/byPosition/:pos"),
};

export const analysisRoutes = {
  getMDSEmbedding: new ApiRoute<undefined, {machine: string; sampleId: string}, {window_size: number}, number[][]>("GET", "/analysis/:machine/:sampleId/clustering"),
}

export const ApiRoutes = {
  ...dbRoutes,
  ...analysisRoutes
};