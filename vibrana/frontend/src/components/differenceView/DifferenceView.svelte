<script lang="ts">
    import type {Fingerprint} from "@lib/types";

    interface Props {
        fingerprints: Fingerprint[];
        width?: number;
        height?: number;
    }

    let { fingerprints, width = 1000, height = 100 }: Props = $props();
</script>