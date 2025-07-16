import {ApiRoute} from "./ApiRoute";
import type { DefaultAppResponse, HyperplaneVector, Config, DistributionWeights } from '@lib/types';

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

export const genericRoutes = {
  getConfig: new ApiRoute<undefined, undefined, undefined, Config>("GET", "/config"),
}

export const dbRoutes = {
  getSlice: new ApiRoute<undefined, { dataset: string; subset: string; }, { start_index?: number; end_index?: number }, number[]>("GET", "/db/:dataset/:subset/slice"),
  getVectors: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, HyperplaneVector[]>("GET", "/db/:dataset/:subset/vectors"),
  getVector: new ApiRoute<undefined, { dataset: string; subset: string; }, { start_index: number; slice_index: number }, HyperplaneVector>("GET", "/db/:dataset/:subset/vector"),
  clearVectors: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/clear"),
  getWeights: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, DistributionWeights>("GET", "/db/:dataset/:subset/weights"),
  storeWeights: new ApiRoute<DistributionWeights, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/weights"),
};

export const computingRoutes = {
  computeSingleStep: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, HyperplaneVector>("POST", "/computing/:dataset/:subset/single_step"),
  setTargetThreads: new ApiRoute<{ threads: number }, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/computing/:dataset/:subset/set_target_threads"),
  getTargetThreads: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, number>("GET", "/computing/:dataset/:subset/get_target_threads"),
}


export const ApiRoutes = {
  ...genericRoutes,
  ...dbRoutes,
  ...computingRoutes
};