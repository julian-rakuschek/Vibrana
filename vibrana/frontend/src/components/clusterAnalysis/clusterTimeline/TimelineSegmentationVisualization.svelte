<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from '@lib/types';
    import {onDestroy, onMount} from 'svelte';
    import {type AVLNode, AVLTree} from "avl";
    import {findNearestFingerprint} from "@lib/helper/util";
    import {fingerprintMode} from "@lib/stores";
    import type IntervalTree from "node-interval-tree";
    import {computeVisibleIndices, indexListForDensityPlot} from "@lib/helper/fingerprintHelper";
    import {density1d} from 'fast-kde';

    interface Props {
        colorMapping: ClusterColorMapping;
        visibleIndices?: number[];
        width?: number;
        height?: number;
        bar_height_based_on_density?: boolean;
        fp_tree: AVLTree<number, Fingerprint>;
        fp_interval_tree: IntervalTree<Fingerprint>;
    }

    let {colorMapping, visibleIndices = [], width = 1000, fp_tree, fp_interval_tree, bar_height_based_on_density = true, height = 100}: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;

    type VerticalBarElement = {
        label: number;
        y: number;
        height: number;
    }

    function getIntervalCounts(visibleIndices: number[]) {
        const counts: number[] = [];
        for (let i = 0; i < width; i++) {
            const fp_count = fp_interval_tree.search(visibleIndices[i], visibleIndices[i + 1]).length
            for (let j = 0; j < fp_count; j++) {
                counts.push(i);
            }
        }
        return counts;
    }

    function computeBarHeights(visibleIndices: number[]) {
        const density_input = getIntervalCounts(visibleIndices);
        if (density_input.length === 0) {
            return new Array(width).fill(0.05 * height)
        }
        const visible_densities: number[] = density1d(density_input, {bins: width, extent: [0, width], bandwidth: 50}).grid();
        const max_density = Math.max(...visible_densities);
        const densities = visible_densities.map(d => d / max_density);
        return densities.map(d => Math.max(0.05 * height, d * height));
    }

    function label_distribution(fingerprints: Fingerprint[], feature: "tde" | "psd", baseline_y: number, height: number): VerticalBarElement[] {
        const labelCounts: Record<number, number> = {};
        fingerprints.forEach(fp => {
            labelCounts[fp.label[feature]] = (labelCounts[fp.label[feature]] || 0) + 1;
        });
        const result: VerticalBarElement[] = []
        let current_baseline = baseline_y;
        for (const label of Object.keys(labelCounts)) {
            const count = labelCounts[label];
            const relative = count / fingerprints.length;
            result.push({ label: label, y: current_baseline, height: height * relative  })
            current_baseline -= height * relative;
        }
        return result;
    }

    function render(visibleIndices: number[], feature: "tde" | "psd") {
        if (!canvas || !context) return;
        context.clearRect(0, 0, width, height);
        const heights = computeBarHeights(visibleIndices);
        for (let i = 0; i < width; i++) {
            const fingerprints: Fingerprint[] = fp_interval_tree.search(visibleIndices[i], visibleIndices[i+1])
            const local_height = bar_height_based_on_density ? heights[i] : height;
            if (fingerprints.length > 0) {
                const label_dist = label_distribution(fingerprints, feature, height, local_height)
                context.globalAlpha = 1;
                for (const verticalBarElement of label_dist) {
                    context.fillStyle = colorMapping[verticalBarElement.label]
                    context.fillRect(i, verticalBarElement.y, 1, -verticalBarElement.height);
                }
            } else {
                const label = findNearestFingerprint(visibleIndices[i], fp_tree)?.label[feature] ?? null;
                context.globalAlpha = 0.2;
                context.fillStyle = label === null ? 'lightgray' : colorMapping[label];
                context.fillRect(i, height, 1, -local_height);
            }
        }
    }

    onMount(async () => {
        if (!canvas) return;
        context = canvas.getContext('2d');
        render(visibleIndices, $fingerprintMode);
    });

    $effect(() => {
        render(visibleIndices, $fingerprintMode);
    });


</script>

<canvas {height} {width} bind:this={canvas}></canvas>