import {createQuery, type QueryKey, type CreateQueryOptions, type CreateQueryResult} from '@tanstack/svelte-query'
import type {ApiRoute} from "@lib/api/ApiRoute";
import type {AppResponse} from "@lib/types";
import {getResolvedUrl, type IRequestObject} from "@lib/api/QueryHelpers";
import {sessionGetAll, sessionGetLabelCount, sessionGetLabels, sessionGetNormals} from "@lib/helper/sessionStorageHelper";

export type MultiRequestPart<TRequestData, TRequestParams, TQueryParams, TResponse extends AppResponse<any>> =
    { apiRoute: ApiRoute<TRequestData, TRequestParams, TQueryParams, TResponse>; requestObject?: IRequestObject<TRequestData, TRequestParams, TQueryParams> };

function getQueryParams<TRequestData, TRequestParams, TQueryParams, TResponse extends AppResponse<any>>(requestObj: MultiRequestPart<TRequestData, TRequestParams, TQueryParams, TResponse>, ro?: boolean): CreateQueryOptions<TResponse> {
    const {apiRoute, requestObject = {}} = requestObj;

    const queryKey: QueryKey = [getResolvedUrl(apiRoute.url, requestObject, true)];


    async function queryFn(): Promise<TResponse> {
        if (
            (apiRoute.url === "/analysis/:dataset/:subset/:chunk/distanceProfile/quantized" ||
                apiRoute.url === "/analysis/:dataset/:subset/normal_tube" ||
                apiRoute.url === "/analysis/:dataset/:subset/anomaly_metrics") && apiRoute.method === "POST"
        ) {
            // @ts-ignore
            requestObject.data = sessionGetAll(requestObject.params.dataset, requestObject.params.subset)
        }
        if (apiRoute.url === "/db/:dataset/:subset/normals" && ro) {
            // @ts-ignore
            return sessionGetNormals(requestObject.params.dataset, requestObject.params.subset)
        }
        if (apiRoute.url === "/db/:dataset/:subset/:chunk/labels" && ro) {
            // @ts-ignore
            return sessionGetLabels(requestObject.params.dataset, requestObject.params.subset, requestObject.params.chunk)
        }
        if (apiRoute.url === "/db/:dataset/:subset/labels/count" && ro) {
            // @ts-ignore
            return sessionGetLabelCount(requestObject.params.dataset, requestObject.params.subset)
        }
        return apiRoute.fetch(requestObject);
    }

    return {
        queryFn,
        queryKey,
    };
}

export function useQueryFetch<TRequestData, TRequestParams, TQueryParams, TResponse>(
    apiRoute: ApiRoute<TRequestData, TRequestParams, TQueryParams, TResponse>,
    requestObject: IRequestObject<TRequestData, TRequestParams, TQueryParams> = {},
    refetchInterval?: number,
    customQueryKey?: QueryKey,
    ro?: boolean
): CreateQueryResult<TResponse, Error> {
    const queryParams = getQueryParams<TRequestData, TRequestParams, TQueryParams, TResponse>({apiRoute, requestObject}, ro);

    return createQuery<TResponse>({
        queryKey: customQueryKey ? customQueryKey : queryParams.queryKey,
        queryFn: queryParams.queryFn,
        refetchInterval: refetchInterval ?? false
    })
}