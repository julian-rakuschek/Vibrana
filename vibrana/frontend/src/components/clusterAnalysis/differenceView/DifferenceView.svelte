<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import {computeAveragePsdSegments} from "@lib/helper/fingerprintHelper";
    import PeriodogramBar from "@components/clusterAnalysis/differenceView/PeriodogramBar.svelte";

    interface Props {
        fingerprints: Fingerprint[];
        width?: number;
        colorMapping: ClusterColorMapping;
    }

    let {fingerprints, width = 1000, colorMapping}: Props = $props();

    let averagePsdSegments = $derived(computeAveragePsdSegments(fingerprints));
</script>

<div>
    {#each averagePsdSegments as segment}
        <PeriodogramBar color={colorMapping[segment.label]} periodogram={segment.averagePsd} />
    {/each}
</div>
