<script lang="ts">
    import {type ClusterColorMapping, type Fingerprint} from "@lib/types";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {AVLTree} from "avl";
    import FingerprintDetailView from "@components/clusterAnalysis/differenceView/FingerprintDetailView.svelte";
    import FingerprintDifference from "@components/clusterAnalysis/differenceView/FingerprintDifference.svelte";
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

    type SelectedFingerprint = {
        actualIndex: number;
        fingerprint: Fingerprint;
        averagePSD: number[];
    };

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

    function getSelectedFingerprints(selectedIndices: number[], signalLength: number): SelectedFingerprint[] {
        return selectedIndices
            .toSorted()
            .map((selectedIndex) => {
                const actualIndex = parameterToSignalIndex(selectedIndex, signalLength);
                const fingerprint = findNearestFingerprint(actualIndex, fp_tree);

                if (!fingerprint) return null;

                return {
                    actualIndex,
                    fingerprint,
                    averagePSD: computeAveragePSD(fingerprint.label[$fingerprintMode], $fingerprintMode)
                };
            })
            .filter((entry): entry is SelectedFingerprint => entry !== null);
    }

</script>

{#if selectedIndices.length > 0}
    <div class="flex gap-4 overflow-x-auto justify-center">
        {#await dataProvider.get_length() then signalLength}
            {@const selectedFingerprints = getSelectedFingerprints(selectedIndices, signalLength)}
            {#if selectedFingerprints.length === 2}
                {@const first = selectedFingerprints[0]}
                {@const second = selectedFingerprints[1]}
                <FingerprintDetailView
                        fingerprint={first.fingerprint}
                        {dataProvider}
                        actualIndex={first.actualIndex}
                        {colorMapping}
                        averagePSD={first.averagePSD}
                />
                <FingerprintDifference
                        fingerprint1={first.fingerprint}
                        fingerprint2={second.fingerprint}
                        averagePSD1={first.averagePSD}
                        averagePSD2={second.averagePSD}
                />
                <FingerprintDetailView
                        fingerprint={second.fingerprint}
                        {dataProvider}
                        actualIndex={second.actualIndex}
                        {colorMapping}
                        averagePSD={second.averagePSD}
                />
            {:else}
                {#each selectedFingerprints as selectedFingerprint}
                    <FingerprintDetailView
                            fingerprint={selectedFingerprint.fingerprint}
                            {dataProvider}
                            actualIndex={selectedFingerprint.actualIndex}
                            {colorMapping}
                            averagePSD={selectedFingerprint.averagePSD}
                    />
                {/each}
            {/if}
        {/await}
    </div>
{/if}
