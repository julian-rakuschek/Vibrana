<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import {AVLTree} from "avl";
    import {findNearestFingerprint} from "@lib/helper/util";
    import {fingerprintMode} from "@lib/stores";
    import type IntervalTree from "node-interval-tree";

    interface Props {
        colorMapping: ClusterColorMapping;
        visibleIndices?: number[];
        width?: number;
        fp_tree: AVLTree<number, Fingerprint>;
        fp_interval_tree: IntervalTree<Fingerprint>;
    }

    let {colorMapping, visibleIndices = [], width = 1000, fp_tree, fp_interval_tree}: Props = $props();

    let canvas: HTMLCanvasElement | undefined = $state();
    let context: CanvasRenderingContext2D | null;
    const height = 100;

    type VerticalBarElement = {
        label: number;
        y: number;
        height: number;
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
        for (let i = 0; i < width; i++) {
            const fingerprints: Fingerprint[] = fp_interval_tree.search(visibleIndices[i], visibleIndices[i+1])
            if (fingerprints.length > 0) {
                const label_dist = label_distribution(fingerprints, feature, height, height)
                context.globalAlpha = 1;
                for (const verticalBarElement of label_dist) {
                    context.fillStyle = colorMapping[verticalBarElement.label]
                    context.fillRect(i, verticalBarElement.y, 1, -verticalBarElement.height);
                }
            } else {
                const label = findNearestFingerprint(visibleIndices[i], fp_tree)?.label[feature] ?? null;
                context.globalAlpha = 0.2;
                context.fillStyle = label === null ? 'lightgray' : colorMapping[label];
                context.fillRect(i, 0, 1, height);
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

    fingerprintMode.subscribe(fm => render(visibleIndices, fm));

</script>

<canvas {height} {width} bind:this={canvas}></canvas>