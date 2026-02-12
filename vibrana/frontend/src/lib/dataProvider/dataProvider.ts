import {ApiRoutes} from "@lib/api/ApiRoutes";
import type {Fingerprint} from "@lib/types";
import {type Writable, writable} from "svelte/store";
import {stretchBalanced} from "@lib/helper/util";

export class DataProvider {
    private readonly dataset: string;
    private readonly subset: string;
    private readonly in_memory: boolean;
    public loading: Writable<boolean> = writable(false);
    // only used if in_memory is true
    private vibration_signal: number[] | undefined;

    constructor(dataset: string, subset: string, in_memory: boolean) {
        this.dataset = dataset;
        this.subset = subset;
        this.in_memory = in_memory;
    }

    async load() {
        if (!this.in_memory) throw "only allowed when dataset is configured as in memory";
        this.loading.set(true);
        this.vibration_signal = await ApiRoutes.getSlice.fetch({params: {dataset: this.dataset, subset: this.subset}});
        console.log("Load complete")
        this.loading.set(false);
        return true;
    }

    async get_timestamps(zoom_interval: [number, number], width: number) {
        let start = Math.floor(zoom_interval[0] * this.get_length());
        let end = Math.floor(zoom_interval[1] * this.get_length());
        if (this.get_length() == 0) {
            start = 0;
            end = -1;
        }
        const timestamps = await ApiRoutes.getTimestamps.fetch({
            params: {dataset: this.dataset, subset: this.subset},
            queryParams: {start_index: start, end_index: end, amount: width}
        });
        return stretchBalanced(timestamps, width);
    }

    isInMemory(): boolean {
        return this.in_memory
    };


    get_fingerprint_data_javascript(fp: Fingerprint) {
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

    get_length() {
        return this.vibration_signal?.length ?? 0;
    }
}