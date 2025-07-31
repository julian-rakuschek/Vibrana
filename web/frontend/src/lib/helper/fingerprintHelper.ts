import type {Fingerprint} from "@lib/types";

export function computeIndexAllocationArray(fingerprints: Fingerprint[], width: number, empty_marker: number | null, useLabels: boolean = false) {
    const index_allocation: number[] = new Array(width).fill(empty_marker);
    for (const fp of fingerprints) {
        const start = Math.floor((fp.start_index / fp.max_index) * width);
        const rectangle_width = Math.floor((fp.slice_length / fp.max_index) * width);
        for (let j = 0; j < rectangle_width; j++) index_allocation[start + j] = useLabels ? fp.label : fp.index;
    }
    return index_allocation;
}


export function allocatedIndexList(fingerprints: Fingerprint[], width: number) {
    const index_counts: number[] = []
    for (const fp of fingerprints) {
        const start = Math.floor((fp.start_index / fp.max_index) * width);
        const rectangle_width = Math.floor((fp.slice_length / fp.max_index) * width);
        for (let j = 0; j < rectangle_width; j++) index_counts.push(start + j)
    }
    return index_counts;
}