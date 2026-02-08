import { intervalToDuration, formatDuration } from "date-fns";

export function classNames(...classes: string[]): string {
    return classes.filter(Boolean).join(" ");
}

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


export function padArray<T>(arr: T[], n: number): T[] {
    const firstElement = arr[0];
    const lastElement = arr[arr.length - 1];
    const frontPadding = Array(Math.floor(n / 2)).fill(firstElement);
    const backPadding = Array(Math.ceil(n / 2)).fill(lastElement);
    return [...frontPadding, ...arr, ...backPadding];
}

export function colorIsDarkSimple(bgColor: string): boolean {
    const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
    const r = parseInt(color.substring(0, 2), 16); // hexToR
    const g = parseInt(color.substring(2, 4), 16); // hexToG
    const b = parseInt(color.substring(4, 6), 16); // hexToB
    return ((r * 0.299) + (g * 0.587) + (b * 0.114)) <= 186;
}

export function randomWalk(n: number): number[] {
    const series: number[] = [0]; // Initialize the series with the starting value 0

    for (let i = 1; i < n; i++) {
        // Randomly choose either +1 or -1
        const step = Math.random() < 0.5 ? -1 : 1;
        // Add the step to the previous value to get the new value
        series.push(series[i - 1] + step);
    }

    return series;
}


export function isNullOrUndef(value: unknown): value is null | undefined {
    return value === null || typeof value === 'undefined';
}

export function minMaxDecimation(data: number[], availableWidth: number) {
    let avgX = 0;
    let countX = 0;
    let i = 0;
    let point = 0;
    let x = 0;
    let y = 0;
    let prevX = -1; // Initialize to a value that won't match any `truncX` in the first iteration
    let minIndex = -1;
    let maxIndex = -1;
    let startIndex = 0;
    let minY = Number.POSITIVE_INFINITY;
    let maxY = Number.NEGATIVE_INFINITY;
    const decimated: number[] = [];

    const data_length = data.length;

    for (i = 0; i < data_length; ++i) {
        x = i / data_length * availableWidth;
        y = data[i];
        const truncX = x | 0;

        if (truncX === prevX) {
            // Determine `minY` / `maxY` and `avgX` while we stay within same x-position
            if (y < minY) {
                minY = y;
                minIndex = i;
            } else if (y > maxY) {
                maxY = y;
                maxIndex = i;
            }
            // For first point in group, countX is `0`, so average will be `x` / 1.
            // Use point.x here because we're computing the average data `x` value
            avgX = (countX * avgX + i) / ++countX;
        } else {
            // Push up to 4 points, 3 for the last interval and the first point for this interval
            const lastIndex = i - 1;

            if (!isNullOrUndef(minIndex) && !isNullOrUndef(maxIndex)) {
                // The interval is defined by 4 points: start, min, max, end.
                // The starting point is already considered at this point, so we need to determine which
                // of the other points to add. We need to sort these points to ensure the decimated data
                // is still sorted and then ensure there are no duplicates.
                const intermediateIndex1 = Math.min(minIndex, maxIndex);
                const intermediateIndex2 = Math.max(minIndex, maxIndex);

                if (intermediateIndex1 !== startIndex && intermediateIndex1 !== lastIndex) {
                    decimated.push(data[intermediateIndex1]);
                }
                if (intermediateIndex2 !== startIndex && intermediateIndex2 !== lastIndex) {
                    decimated.push(data[intermediateIndex2]);
                }
            }

            // lastIndex === startIndex will occur when a range has only 1 point which could
            // happen with very uneven data
            if (i > 0 && lastIndex !== startIndex) {
                // Last point in the previous interval
                decimated.push(data[lastIndex]);
            }

            // Start of the new interval
            decimated.push(point);
            prevX = truncX;
            countX = 0;
            minY = maxY = y;
            minIndex = maxIndex = startIndex = i;
        }
    }

    return decimated;
}

export function stretchBalanced<T>(arr: readonly T[], targetLen: number): T[] {
      const n = arr.length;
      if (n === 0) return [];
      if (targetLen <= 0) return [];

      const base = Math.floor(targetLen / n);
      const rem = targetLen % n;

      const out: T[] = [];
      for (let i = 0; i < n; i++) {
        const repeats = base + (i < rem ? 1 : 0);
        for (let r = 0; r < repeats; r++) out.push(arr[i]);
      }
      return out;
}

export function formatUnixTimestamp(timestamp: number): { isoDate: string; time: string;} {
        const date = timestamp < 1e12 ? new Date(timestamp * 1000) : new Date(timestamp);
        const isoDate = date.toISOString();
        const time = isoDate.split("T")[1].replace("Z", "");
        return {isoDate: isoDate.split("T")[0], time};
}

export function humanTimeSpan(timestamps: number[]): string {
    if (timestamps.length < 2) return "No time span available"
    const ts1 = timestamps[0] < 1e12 ? timestamps[0] * 1000 : timestamps[0];
    const ts2 = timestamps[timestamps.length - 1] < 1e12 ? timestamps[timestamps.length - 1] * 1000 : timestamps[timestamps.length - 1];

    const duration = intervalToDuration({
      start: new Date(ts1),
      end: new Date(ts2),
    });

    return formatDuration(duration);
}