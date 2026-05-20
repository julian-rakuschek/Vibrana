import {ApiRoutes} from "@lib/api/ApiRoutes";
import type {Fingerprint, TimeInformation} from "@lib/types";
import {type Writable, writable} from "svelte/store";
import {estimateTimestamp, generateTimestamps} from "@lib/helper/util";

export class DataProvider {
    private readonly dataset: string;
    private readonly subset: string;
    private readonly in_memory: boolean;
    public loading: Writable<boolean> = writable(false);
    private time_information: TimeInformation | undefined;
    // only used if in_memory is true
    private vibration_signal: number[] | undefined;

    constructor(dataset: string, subset: string, in_memory: boolean) {
        this.dataset = dataset;
        this.subset = subset;
        this.in_memory = in_memory;
    }

    async load() {
        this.loading.set(true);
        this.time_information = await ApiRoutes.getTimeInformation.fetch({params: {dataset: this.dataset, subset: this.subset}});

        if (!this.in_memory) {
            this.loading.set(false);
            return true;
        }
        this.vibration_signal = await ApiRoutes.getSlice.fetch({params: {dataset: this.dataset, subset: this.subset}});
        console.log("Load complete")
        this.loading.set(false);
        return true;
    }

    async get_timestamps(zoom_interval: [number, number], width: number) {
        if (!this.time_information) {
            this.time_information = await ApiRoutes.getTimeInformation.fetch({params: {dataset: this.dataset, subset: this.subset}});
        }
        return generateTimestamps(this.time_information?.start_time ?? "1970-01-01T00:00:00", this.time_information?.end_time ?? "1970-01-01T23:59:00", width, zoom_interval);
    }

    async estimate_timestamp(index: number) {
        if (!this.time_information) {
            this.time_information = await ApiRoutes.getTimeInformation.fetch({params: {dataset: this.dataset, subset: this.subset}});
        }
        return estimateTimestamp(this.time_information?.start_time ?? "1970-01-01T00:00:00", this.time_information?.end_time ?? "1970-01-01T23:59:00", index, this.time_information.total_sample_points);
    }

    isInMemory(): boolean {
        return this.in_memory
    };


    compute_in_memory_projection(fp: Fingerprint) {
        if (!this.in_memory) throw "only available when dataset is configured as in memory";
        if (!this.vibration_signal) {
            console.warn("Vibration signal has not been loaded, returning empty projection.")
            return [];
        }
        const projected: number[][] = []
        for (let i = 0; i < fp.slice_length - fp.sliding_window_size; i++) {
            const window = this.vibration_signal.slice(fp.start_index + i, fp.start_index + i + fp.sliding_window_size);
            let x = 0, y = 0;
            for (let j = 0; j < window.length; j++) {
                x += window[j] * fp.v1[j];
                y += window[j] * fp.v2[j];
            }
            projected.push([x, y]);
        }
        return projected;
    }

    async fetch_projection(fp: Fingerprint) {
        return await ApiRoutes.computeProjection.fetch({
            params: {dataset: this.dataset, subset: this.subset},
            data: fp
        });
    }

    async get_length() {
        if (!this.time_information) {
            this.time_information = await ApiRoutes.getTimeInformation.fetch({params: {dataset: this.dataset, subset: this.subset}});
        }
        return this.time_information.total_sample_points;
    }
}
