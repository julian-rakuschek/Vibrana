import {createQuery, type QueryKey, type CreateQueryOptions, type CreateQueryResult} from '@tanstack/svelte-query'
import type {ApiRoute} from "@lib/api/ApiRoute";
import type {AppResponse} from "@lib/types";
import {getResolvedUrl, type IRequestObject} from "@lib/api/QueryHelpers";
import {sessionGetLabels, sessionGetNormals} from "@lib/helper/sessionStorageHelper";

export type MultiRequestPart<TRequestData, TRequestParams, TQueryParams, TResponse extends AppResponse<any>> =
    { apiRoute: ApiRoute<TRequestData, TRequestParams, TQueryParams, TResponse>; requestObject?: IRequestObject<TRequestData, TRequestParams, TQueryParams> };

function getQueryParams<TRequestData, TRequestParams, TQueryParams, TResponse extends AppResponse<any>>(requestObj: MultiRequestPart<TRequestData, TRequestParams, TQueryParams, TResponse>, ro?: boolean): CreateQueryOptions<TResponse> {
    const {apiRoute, requestObject = {}} = requestObj;

    const queryKey: QueryKey = [getResolvedUrl(apiRoute.url, requestObject, true)];


    async function queryFn(): Promise<TResponse> {
        if (apiRoute.url === "/db/normals/:machineId" && ro) {
            // @ts-ignore
            return sessionGetNormals(requestObject.params.machineId)
        }
        if (apiRoute.url === "/db/labels/:machineId/:sampleId" && ro) {
            // @ts-ignore
            return sessionGetLabels(requestObject.params.machineId, requestObject.params.sampleId)
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