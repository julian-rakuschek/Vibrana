import { intervalToDuration, formatDuration } from "date-fns";




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