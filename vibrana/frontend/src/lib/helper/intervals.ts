export function mergeIntervals(intervals_to_merge: [number, number][]): [number, number][] {
    intervals_to_merge.sort((a, b) => a[0] - b[0]);
    const merged = [];

    for (const interval of intervals_to_merge) {
        if (!merged.length || interval[0] > merged[merged.length - 1][1]) {
            merged.push(interval);
        } else {
            merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], interval[1]);
        }
    }

    return merged;
}

export function deleteInterval(intervals_to_delete_from: [number, number][], to_delete: [number, number]): [number, number][] {
    intervals_to_delete_from.sort((a, b) => a[0] - b[0]);
    let filtered_intervals: [number, number][] = [];

    for (const interval of intervals_to_delete_from) {
        if (interval[0] > to_delete[0] && interval[1] < to_delete[1]) continue;
        else if (interval[0] <= to_delete[0] && interval[1] <= to_delete[0]) filtered_intervals.push(interval);
        else if (interval[0] >= to_delete[1] && interval[1] >= to_delete[1]) filtered_intervals.push(interval);
        else if (interval[0] < to_delete[0] && interval[1] > to_delete[1]) {
            filtered_intervals.push([interval[0], to_delete[0]]);
            filtered_intervals.push([to_delete[1], interval[1]]);
        } else if (interval[0] < to_delete[0]) filtered_intervals.push([interval[0], to_delete[0]]);
        else if (interval[1] > to_delete[1]) filtered_intervals.push([to_delete[1], interval[1]]);
    }

    return filtered_intervals;
}