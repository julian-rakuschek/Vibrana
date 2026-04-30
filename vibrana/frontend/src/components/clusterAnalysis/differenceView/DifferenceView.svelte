<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import {computeAveragePsdSegments} from "@lib/helper/fingerprintHelper";
    import PeriodogramBar from "@components/clusterAnalysis/differenceView/PeriodogramBar.svelte";
    import DifferenceBand from "@components/clusterAnalysis/differenceView/DifferenceBand.svelte";

    interface Props {
        fingerprints: Fingerprint[];
        width?: number;
        colorMapping: ClusterColorMapping;
    }

    let {fingerprints, width = 1000, colorMapping}: Props = $props();

    let averagePsdSegments = $derived(computeAveragePsdSegments(fingerprints));
</script>

<div>
    {#each averagePsdSegments as segment, index}
        <PeriodogramBar color={colorMapping[segment.label]} periodogram={segment.averagePsd} height={50} width={width} />
        {#if index < averagePsdSegments.length - 1}
            <DifferenceBand
                periodogram1={segment.averagePsd}
                periodogram2={averagePsdSegments[index + 1].averagePsd}
                height={50}
                {width}
            />
        {/if}
    {/each}
</div>
