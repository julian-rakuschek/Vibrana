import {ApiRoutes} from "@lib/api/ApiRoutes";
import type {Fingerprint} from "@lib/types";

export class DataProvider {
    private dataset: string;
    private subset: string;
    private w: number;
    private in_memory: boolean;
    // only used if in_memory is true
    private vibration_signal: number[] | undefined;

    constructor(dataset: string, subset: string, w: number, in_memory: boolean) {
        this.dataset = dataset;
        this.subset = subset;
        this.w = w;
        this.in_memory = in_memory;
    }

    async load() {
        if (!this.in_memory) throw "only allowed when dataset is configured as in memory";
        this.vibration_signal = await ApiRoutes.getSlice.fetch({params: {dataset: this.dataset, subset: this.subset}});
        console.log("Load complete")
    }


    get_fingerprint_data_javascript(hyperplane: Fingerprint) {
        if (!this.in_memory) throw "only available when dataset is configured as in memory";
        if (!this.vibration_signal) {
            console.warn("Vibration signal has not been loaded, returning empty projection.")
            return [];
        }
        const projected: number[][] = []
        for (let i = 0; i < hyperplane.slice_length - this.w; i++) {
            const window = this.vibration_signal.slice(hyperplane.start_index + i, hyperplane.start_index + i + this.w);
            let x = 0, y = 0;
            for (let j = 0; j < window.length; j++) {
                x += window[j] * hyperplane.v1[j];
                y += window[j] * hyperplane.v2[j];
            }
            projected.push([x, y]);
        }
        return projected;
    }

    async get_fingerprint_image(hyperplane: Fingerprint) {

    }

    async get_slice(start_index: number, end_index: number): Promise<number[]> {
        if (this.in_memory && this.vibration_signal) {
            return this.vibration_signal.slice(start_index, end_index);
        }
        else {
            return await ApiRoutes.getSlice.fetch({ params: { dataset: this.dataset, subset: this.subset }, queryParams: { start_index, end_index }})
        }
    }
}