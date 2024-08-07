import {ApiRoute} from "lib/api/ApiRoute";
import {Annotation} from "../../types";

// ApiRoute types:
// TRequestData, TRequestParams, TQueryParams, TResponse
//
// (1) TRequestData = Post data
// (2) TRequestParams = things that go into the url, e.g. /mongodb/data/:bucket then TRequestParams would be {bucket: string}
// (3) TQueryParams = Everything that comes after the url, e.g. /some?query=value, then TQueryParams would be {query: string}
// (4) TResponse = Response object

export const dbRoutes = {
  getDummyValues: new ApiRoute<undefined, undefined, undefined, number[]>("GET", "/db/dummy_values"),
  getDummyProjected: new ApiRoute<undefined, undefined, undefined, number[][]>("GET", "/db/dummy_projected"),
  getLabels: new ApiRoute<undefined, {series: string}, undefined, Annotation[]>("GET", "/db/labels/:series"),
  addLabel: new ApiRoute<Annotation, {series: string}, undefined, undefined>("POST", "/db/labels/:series"),
  deleteLabel: new ApiRoute<{index: number}, {series: string}, undefined, undefined>("DELETE", "/db/labels/:series"),
};

export const ApiRoutes = {
  ...dbRoutes,
};