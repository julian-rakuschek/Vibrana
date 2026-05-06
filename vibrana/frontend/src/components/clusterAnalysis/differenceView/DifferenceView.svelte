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
        averageFFT: number[];
    };

    function parameterToSignalIndex(t: number, signalLength: number) {
        if (signalLength <= 0) return 0;
        return Math.min(Math.max(Math.floor(t * signalLength), 0), signalLength - 1);
    }

    function computeAverageFFT(label: number, fingerprintMode: "tde" | "fft"): number[] {
        const cluster = fingerprints
            .filter(f => f.label[fingerprintMode] === label)
            .map(f => f.feature_descriptors.fft.magnitudes);

        if (cluster.length === 0) return [];

        const fftLength = cluster[0].length;
        const sums = new Array(fftLength).fill(0);

        for (const fft of cluster) {
            for (let i = 0; i < fftLength; i++) {
                sums[i] += fft[i] ?? 0;
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
                    averageFFT: computeAverageFFT(fingerprint.label[$fingerprintMode], $fingerprintMode)
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
                <div class="relative flex gap-4">
                    <div
                            class="pointer-events-none absolute left-1/2 -translate-x-1/2 w-1/4 top-1/2 h-64 -translate-y-1/2 opacity-20"
                            style={`clip-path: polygon(0 38%, calc(100% - 92px) 38%, calc(100% - 92px) 24%, 100% 50%, calc(100% - 92px) 76%, calc(100% - 92px) 62%, 0 62%); background: linear-gradient(90deg, ${colorMapping[first.fingerprint.label[$fingerprintMode]]}, ${colorMapping[second.fingerprint.label[$fingerprintMode]]});`}
                    ></div>
                    <div class="relative z-10">
                        <FingerprintDetailView
                                fingerprint={first.fingerprint}
                                {dataProvider}
                                actualIndex={first.actualIndex}
                                {colorMapping}
                                averageFFT={first.averageFFT}
                        />
                    </div>
                    <div class="relative z-10">
                        <FingerprintDifference
                                fingerprint1={first.fingerprint}
                                fingerprint2={second.fingerprint}
                                averageFFT1={first.averageFFT}
                                averageFFT2={second.averageFFT}
                        />
                    </div>
                    <div class="relative z-10">
                        <FingerprintDetailView
                                fingerprint={second.fingerprint}
                                {dataProvider}
                                actualIndex={second.actualIndex}
                                {colorMapping}
                                averageFFT={second.averageFFT}
                        />
                    </div>
                </div>
            {:else}
                {#each selectedFingerprints as selectedFingerprint}
                    <FingerprintDetailView
                            fingerprint={selectedFingerprint.fingerprint}
                            {dataProvider}
                            actualIndex={selectedFingerprint.actualIndex}
                            {colorMapping}
                            averageFFT={selectedFingerprint.averageFFT}
                    />
                {/each}
            {/if}
        {/await}
    </div>
{/if}
