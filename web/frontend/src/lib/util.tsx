import { RefObject, useEffect, useMemo, useState } from "react";
import {Annotation} from "../types";
import {b} from "vite/dist/node/types.d-aGj9QkWt";

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