import type {Fingerprint} from "@lib/types";


function updateAllocationArray(fp: Fingerprint, zoom_interval: [number, number], allocation_array: number[], property_accessor: (fp: Fingerprint) => number) {
    const width = allocation_array.length;
    let relative_start = fp.start_index / fp.max_index;
    let relative_end = relative_start + fp.slice_length / fp.max_index;
    if (relative_end < zoom_interval[0] || relative_start > zoom_interval[1]) return;
    relative_start = (relative_start - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
    relative_end = (relative_end - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
    const start = Math.floor(relative_start * width);
    const end = Math.floor(relative_end * width);

    for (let j = start; j < end; j++) {
        if (start < 0 || end >= allocation_array.length) continue;
        allocation_array[j] = property_accessor(fp);
    }
}

function computeAllocationArray(fingerprints: Fingerprint[], zoom_interval: [number, number], allocation_array: number[], property_accessor: (fp: Fingerprint) => number) {
    for (const fp of fingerprints) {
        updateAllocationArray(fp, zoom_interval, allocation_array, property_accessor);
    }
}

export function computeLabelAllocationArray(fingerprints: Fingerprint[], width: number, zoom_interval: [number, number], feature: "tde" | "psd") {
    let label_allocation: number[] = new Array(width).fill(null);
    computeAllocationArray(fingerprints, zoom_interval, label_allocation, (fp: Fingerprint) => fp.label[feature]);
    return label_allocation;
}


export function computeIndexAllocationArray(fingerprints: Fingerprint[], width: number, zoom_interval: [number, number]) {
    const index_allocation: number[] = new Array(width).fill(-1);
    computeAllocationArray(fingerprints, zoom_interval, index_allocation, (fp: Fingerprint) => fp.index);
    return index_allocation;
}

export function updateIndexAllocationArray(index_allocation: number[], new_fingerprint: Fingerprint, zoom_interval: [number, number]) {
    updateAllocationArray(new_fingerprint, zoom_interval, index_allocation, (fp: Fingerprint) => fp.index);
    return index_allocation;
}


export function indexListForDensityPlot(fingerprints: Fingerprint[], width: number, zoom_interval: [number, number]) {
    const index_counts: number[] = []
    for (const fp of fingerprints) {
        let relative_start = fp.start_index / fp.max_index;
        let relative_end = relative_start + fp.slice_length / fp.max_index;
        if (relative_end < zoom_interval[0] || relative_start > zoom_interval[1]) continue;
        relative_start = (relative_start - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
        relative_end = (relative_end - zoom_interval[0]) / (zoom_interval[1] - zoom_interval[0]);
        const start = Math.floor(relative_start * width);
        const rectangle_width = Math.floor((fp.slice_length / fp.max_index) * width);
        for (let j = 0; j < rectangle_width; j++) index_counts.push(start + j)
    }
    return index_counts;
}