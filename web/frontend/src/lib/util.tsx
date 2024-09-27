import {RefObject, useEffect, useMemo, useState} from "react";
import {Annotation} from "../types";

export function classNames(...classes: string[]): string {
    return classes.filter(Boolean).join(" ");
}

export function useOnScreen(ref: RefObject<HTMLElement>) {

    const [isIntersecting, setIntersecting] = useState(false)

    const observer = useMemo(() => new IntersectionObserver(
        ([entry]) => setIntersecting(entry.isIntersecting)
    ), [ref])


    useEffect(() => {
        observer.observe(ref.current!)
        return () => observer.disconnect()
    }, [])

    return isIntersecting
}


export function mergeIntervals(intervals: Annotation[]): Annotation[] {
    intervals.sort((a, b) => a.from - b.from);

    const merged = [];

    for (const interval of intervals) {
        if (!merged.length || interval.from > merged[merged.length - 1].to) {
            merged.push(interval);
        } else {
            merged[merged.length - 1].to = Math.max(merged[merged.length - 1].to, interval.to);
            merged[merged.length - 1].color = (merged[merged.length - 1].color + interval.color) / 2;
        }
    }

    return merged;
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


export function largestTriangleThreeBuckets(data: number[], threshold: number) {
    /**
     * Implementation of the Largest Triangle Three Buckets algorithm.
     *
     * This implementation is based on the original implementation by Sveinn Steinarsson
     * in https://github.com/sveinn-steinarsson/flot-downsample/blob/master/jquery.flot.downsample.js
     *
     * The original implementation is MIT licensed.
     */
    const data_length = data.length;
    if (threshold >= data_length || threshold === 0) {
        return data; // Nothing to do
    }

    const sampled = [];
    let sampled_index = 0;

    // Bucket size. Leave room for start and end data points
    const every = (data_length - 2) / (threshold - 2);

    let a = 0,  // Initially a is the first point in the triangle
        max_area_point,
        max_area,
        area,
        next_a;

    sampled[sampled_index++] = data[a]; // Always add the first point

    for (let i = 0; i < threshold - 2; i++) {

        // Calculate point average for next bucket (containing c)
        let avg_x = 0,
            avg_y = 0,
            avg_range_start = Math.floor((i + 1) * every) + 1,
            avg_range_end = Math.floor((i + 2) * every) + 1;
        avg_range_end = avg_range_end < data_length ? avg_range_end : data_length;

        const avg_range_length = avg_range_end - avg_range_start;

        for (; avg_range_start < avg_range_end; avg_range_start++) {
            avg_x += avg_range_start // * 1 enforces Number (value may be Date)
            avg_y += data[avg_range_start]
        }
        avg_x /= avg_range_length;
        avg_y /= avg_range_length;

        // Get the range for this bucket
        let range_offs = Math.floor((i + 0) * every) + 1;
        const range_to = Math.floor((i + 1) * every) + 1;

        // Point a
        const point_a_x = a, // enforce Number (value may be Date)
            point_a_y = data[a];

        max_area = area = -1;

        for (; range_offs < range_to; range_offs++) {
            // Calculate triangle area over three buckets
            area = Math.abs((point_a_x - avg_x) * (data[range_offs] - point_a_y) -
                (point_a_x - range_offs) * (avg_y - point_a_y)
            ) * 0.5;
            if (area > max_area) {
                max_area = area;
                max_area_point = data[range_offs];
                next_a = range_offs; // Next a is this b
            }
        }

        sampled[sampled_index++] = max_area_point; // Pick this point from the bucket
        a = next_a; // This a is the next a (chosen b)
    }

    sampled[sampled_index++] = data[data_length - 1]; // Always add last

    return sampled;
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