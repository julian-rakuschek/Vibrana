import {ApiRoutes} from "@lib/api/ApiRoutes";
export const prerender = false;
export const ssr = false;


/** @type {import('./$types').PageLoad} */
export async function load({params}) {
    const ro = await ApiRoutes.getReadOnly.fetch()

    return {ro};
}