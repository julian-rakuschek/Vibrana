import axios, { type Method } from "axios";
import type { DefaultAppResponse } from "@lib/types";
import { getRequestConfig, type IRequestObject } from "./QueryHelpers";

const axiosClient = axios.create({
  baseURL: "/api",
  withCredentials: true,
});

export class ApiRoute<TRequestData, TRequestParams, TQueryParams, TResponse = DefaultAppResponse> {

  constructor(public readonly method: Method, public readonly url: string) {
  }

  public async fetch(requestObject: IRequestObject<TRequestData, TRequestParams, TQueryParams> = {}): Promise<TResponse> {
    const { method, url } = this;
    try {
      const config = getRequestConfig(method, url, requestObject);

      const { data } = await axiosClient.request<TResponse>(config);
      return data;
    } catch(error) {
      throw error;
    }
  }
}