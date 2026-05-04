<script lang="ts">
    import {type ClusterColorMapping, ColorMode, type Fingerprint} from "@lib/types";

    interface Props {
        fingerprints: Fingerprint[];
        width?: number;
        colorMapping: ClusterColorMapping;
        selectedIndices: number[]
    }

    let {fingerprints, width = 1000, colorMapping, selectedIndices}: Props = $props();

</script>

{#each selectedIndices as index}
    <p>{index}</p>
{/each}