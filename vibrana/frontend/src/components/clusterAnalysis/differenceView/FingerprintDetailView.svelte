<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import FingerprintRendering from "@components/fingerprintRenderer/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import PSDRendering from "@components/fingerprintRenderer/PSDRendering.svelte";
    import {fingerprintMode} from "@lib/stores";

    interface Props {
        fingerprint: Fingerprint;
        dataProvider: DataProvider;
        actualIndex: number;
        colorMapping: ClusterColorMapping;
        averagePSD: number[];
    }

    let {fingerprint, dataProvider, actualIndex, colorMapping, averagePSD}: Props = $props();
</script>

<div class="relative flex flex-col shadow-xl rounded-lg m-3 w-[300px] h-[750px]">
    <div class="absolute opacity-15 w-full h-full  rounded-lg"
         style={`background-color: ${colorMapping[fingerprint.label[$fingerprintMode]]}`}></div>
    <div class="absolute flex flex-col w-full h-full justify-center items-center">
        <p class="text-xs text-black/60 text-center">Index {actualIndex.toLocaleString()}</p>
        <p>PSD</p>
        <PSDRendering
                showAxis
                frequencies={fingerprint.feature_descriptors.psd.f}
                power={fingerprint.feature_descriptors.psd.Pxx_spec}
                color={colorMapping[fingerprint.label[$fingerprintMode]]}
        />
        <p>Average Cluster PSD</p>
        <PSDRendering
                showAxis
                frequencies={fingerprint.feature_descriptors.psd.f}
                power={averagePSD}
                color={colorMapping[fingerprint.label[$fingerprintMode]]}
        />
        <p>Projection</p>
        <FingerprintRendering {fingerprint} {dataProvider} color={colorMapping[fingerprint.label[$fingerprintMode]]} transparent/>
    </div>

</div>