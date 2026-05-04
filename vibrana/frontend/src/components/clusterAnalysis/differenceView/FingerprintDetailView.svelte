<script lang="ts">
    import type {Fingerprint} from "@lib/types";
    import FingerprintRendering from "@components/fingerprintRenderer/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import PSDRendering from "@components/fingerprintRenderer/PSDRendering.svelte";

    interface Props {
        fingerprint: Fingerprint;
        dataProvider: DataProvider;
        actualIndex: number;
    }

    let {fingerprint, dataProvider, actualIndex}: Props = $props();
</script>

<div class="flex flex-col shadow-xl rounded-lg p-3 m-3">
    <p class="text-xs text-black/60 text-center">Index {actualIndex.toLocaleString()}</p>
    <FingerprintRendering {fingerprint} {dataProvider} />
    <PSDRendering
            showAxis
            frequencies={fingerprint.feature_descriptors.psd.f}
            power={fingerprint.feature_descriptors.psd.Pxx_spec}
    />
</div>