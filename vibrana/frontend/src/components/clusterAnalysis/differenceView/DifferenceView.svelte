<script lang="ts">
    import {type ClusterColorMapping, ColorMode, type Fingerprint} from "@lib/types";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {AVLTree} from "avl";
    import FingerprintDetailView from "@components/clusterAnalysis/differenceView/FingerprintDetailView.svelte";
    import {findNearestFingerprint} from "@lib/helper/util";
    import {fingerprintMode} from "@lib/stores";

    interface Props {
        fingerprints: Fingerprint[];
        width?: number;
        colorMapping: ClusterColorMapping;
        selectedIndices: number[];
        dataProvider: DataProvider;
        fp_tree: AVLTree<number, Fingerprint>;
    }

    let {fingerprints, width = 1000, colorMapping, selectedIndices, dataProvider, fp_tree}: Props = $props();

    function parameterToSignalIndex(t: number, signalLength: number) {
        if (signalLength <= 0) return 0;
        return Math.min(Math.max(Math.floor(t * signalLength), 0), signalLength - 1);
    }

    function computeAveragePSD(label: number, fingerprintMode: "tde" | "psd"): number[] {
        const cluster = fingerprints
            .filter(f => f.label[fingerprintMode] === label)
            .map(f => f.feature_descriptors.psd.Pxx_spec);

        if (cluster.length === 0) return [];

        const psdLength = cluster[0].length;
        const sums = new Array(psdLength).fill(0);

        for (const psd of cluster) {
            for (let i = 0; i < psdLength; i++) {
                sums[i] += psd[i] ?? 0;
            }
        }

        return sums.map(sum => sum / cluster.length);
    }


</script>

{#if selectedIndices.length > 0}
    <div class="flex gap-4 overflow-x-auto justify-center">
        {#await dataProvider.get_length() then signalLength}
            {#each selectedIndices.toSorted() as selectedIndex}
                {@const actualIndex = parameterToSignalIndex(selectedIndex, signalLength)}
                {@const fingerprint = findNearestFingerprint(actualIndex, fp_tree)}
                {#if fingerprint}
                    {@const averagePSD = computeAveragePSD(fingerprint.label[$fingerprintMode], $fingerprintMode)}
                    <FingerprintDetailView {fingerprint} {dataProvider} {actualIndex} {colorMapping} {averagePSD}/>
                {/if}
            {/each}
        {/await}
    </div>
{/if}
