<script lang="ts">
    import {type ClusterColorMapping, ColorMode, type Fingerprint} from "@lib/types";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {AVLTree} from "avl";
    import FingerprintDetailView from "@components/clusterAnalysis/differenceView/FingerprintDetailView.svelte";
    import {findNearestFingerprint} from "@lib/helper/util";

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


</script>

{#if selectedIndices.length > 0}
    <div class="flex gap-4 overflow-x-auto">
        {#await dataProvider.get_length() then signalLength}
            {#each selectedIndices as selectedIndex}
                {@const actualIndex = parameterToSignalIndex(selectedIndex, signalLength)}
                {@const fingerprint = findNearestFingerprint(actualIndex, fp_tree)}
                {#if fingerprint}
                    <FingerprintDetailView {fingerprint} {dataProvider} {actualIndex}/>
                {/if}
            {/each}
        {/await}
    </div>
{/if}
