import {ApiRoute} from "./ApiRoute";
import type {
  DefaultAppResponse,
  Fingerprint,
  Config,
  ParameterSettings,
  ClusterDelta, ParameterSettingsUpdate
} from '@lib/types';

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

const genericRoutes = {
  getConfig: new ApiRoute<undefined, undefined, undefined, Config>("GET", "/config"),
}

const dbRoutes = {
  getSlice: new ApiRoute<undefined, { dataset: string; subset: string; }, { start_index?: number; end_index?: number }, number[]>("GET", "/db/:dataset/:subset/slice"),
  getFingerprints: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, Fingerprint[]>("GET", "/db/:dataset/:subset/fingerprints"),
  clearFingerprints: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/clear"),
  getParameters: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, ParameterSettings>("GET", "/db/:dataset/:subset/parameters"),
  storeParameters: new ApiRoute<ParameterSettingsUpdate, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/parameters"),
  getIntervals: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, [number, number][]>("GET", "/db/:dataset/:subset/intervals"),
  storeIntervals: new ApiRoute<[number, number][], { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/db/:dataset/:subset/intervals"),
};

const computingRoutes = {
  computeSingleStep: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, {new_fingerprint: Fingerprint; label_delta: ClusterDelta}>("POST", "/computing/:dataset/:subset/single_step"),
  activateComputing: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/computing/:dataset/:subset/activate"),
  pauseComputing: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/computing/:dataset/:subset/pause"),
  computingStatus: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, boolean>("GET", "/computing/:dataset/:subset/status"),
}

const analysisRoutes = {
  recomputeClusters: new ApiRoute<undefined, { dataset: string; subset: string; }, undefined, DefaultAppResponse>("POST", "/analysis/:dataset/:subset/cluster"),
}


export const ApiRoutes = {
  ...genericRoutes,
  ...dbRoutes,
  ...computingRoutes,
  ...analysisRoutes
};