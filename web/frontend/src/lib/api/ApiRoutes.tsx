import {ApiRoute} from "lib/api/ApiRoute";

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
};

export const ApiRoutes = {
  ...dbRoutes,
};