import {ApiRoutes} from "@lib/api/ApiRoutes";
import createPCA from "@lib/dataProvider/pca";
import type {HyperplaneVector} from "@lib/types";

export class DataProvider {
    private dataset: string;
    private subset: string;
    private w: number;
    private in_memory: boolean;
    // only used if in_memory is true
    private wasm_vibration_signal;
    private wasm;

    constructor(dataset: string, subset: string, w: number, in_memory: boolean) {
        this.dataset = dataset;
        this.subset = subset;
        this.w = w;
        this.in_memory = in_memory;
    }

    async wasm_load() {
        if (!this.in_memory) throw "only allowed when dataset is configured as in memory";
        this.wasm = await createPCA();
        const data = await ApiRoutes.getSlice.fetch({ params: { dataset: this.dataset, subset: this.subset }})
        this.wasm_vibration_signal = new this.wasm.arrayToVec(data);
    }

    async get_fingerprint_data(hyperplane: HyperplaneVector) {
        if (!this.in_memory) throw "only available when dataset is configured as in memory";
        const tde = this.wasm.slidingWindowView(this.wasm_vibration_signal, this.w, hyperplane.start_index, hyperplane.start_index + hyperplane.slice_length);

    }

    async get_fingerprint_image(hyperplane: HyperplaneVector) {

    }

    // async get_slice(start_index: number, end_index: number) {
    //     if (this.in_memory) {
    //         return this.wasm_vibration_signal;
    //     }
    //     else {
    //         return await ApiRoutes.getSlice.fetch({ params: { dataset: this.dataset, subset: this.subset }, queryParams: { start_index, end_index }})
    //     }
    // }
}