import { intervalToDuration, formatDuration } from "date-fns";
import type {AVLNode, AVLTree} from "avl";
import type {Fingerprint} from "@lib/types";


export function generateTimestamps(
    start: string,
    end: string,
    amount: number,
    zoomInterval: [number, number] = [0, 1]
): number[] {
    if (amount <= 0) return [];

    const startSeconds = new Date(start).getTime() / 1000;
    const endSeconds = new Date(end).getTime() / 1000;
    const [zoomStart, zoomEnd] = zoomInterval;

    if (Number.isNaN(startSeconds) || Number.isNaN(endSeconds)) {
        throw new Error("Invalid start or end timestamp");
    }
    if (zoomStart < 0 || zoomEnd > 1 || zoomStart > zoomEnd) {
        throw new Error("Invalid zoom interval");
    }

    const totalDuration = endSeconds - startSeconds;
    const visibleStart = startSeconds + totalDuration * zoomStart;
    const visibleEnd = startSeconds + totalDuration * zoomEnd;

    if (amount === 1) return [visibleStart];

    const step = (visibleEnd - visibleStart) / (amount - 1);
    return Array.from({ length: amount }, (_, index) => visibleStart + step * index);
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


export function findNearestFingerprint(query: number, tree: AVLTree<number, Fingerprint>): Fingerprint | null {
        let node = tree.root;
        let best: AVLNode<number, Fingerprint> | null = null;

        while (node) {
            const currentDistance = Math.abs(node.key - query);
            const bestDistance = best === null ? Infinity : Math.abs(best.key - query);
            const isCloser = currentDistance < bestDistance;
            const isTieWithSmallerKey =
                currentDistance === bestDistance &&
                best !== null &&
                node.key < best.key;

            if (best === null || isCloser || isTieWithSmallerKey) best = node;
            if (query === node.key) return node.data ?? null;
            node = query < node.key ? node.left : node.right;
        }

        return best?.data ?? null;
    }