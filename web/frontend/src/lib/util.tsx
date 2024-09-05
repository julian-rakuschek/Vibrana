import { RefObject, useEffect, useMemo, useState } from "react";
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
