<script lang="ts">
    import type {ClusterColorMapping, Fingerprint} from "@lib/types";
    import FingerprintRendering from "@components/fingerprintRenderer/FingerprintRendering.svelte";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import FFTRendering from "@components/fingerprintRenderer/FFTRendering.svelte";
    import {fingerprintMode} from "@lib/stores";
    import {estimateTimestamp, formatUnixTimestamp} from "@lib/helper/util";

    interface Props {
        fingerprint: Fingerprint;
        dataProvider: DataProvider;
        actualIndex: number;
        colorMapping: ClusterColorMapping;
        averageFFT: number[];
    }

    let {fingerprint, dataProvider, actualIndex, colorMapping, averageFFT}: Props = $props();
    let timestamp = $derived(dataProvider.estimate_timestamp(fingerprint.start_index));
</script>

<div class="relative flex flex-col shadow-xl rounded-lg m-3 w-[400px] h-[800px]">
    <div class="absolute opacity-15 w-full h-full  rounded-lg"
         style={`background-color: ${colorMapping[fingerprint.label[$fingerprintMode]]}`}></div>
    <div class="absolute flex flex-col w-full h-full justify-center items-center gap-5">
        <div class="text-xs text-black/60 text-center">
            <p>Index {fingerprint.start_index}</p>
            {#await timestamp then ts}
                <p>{formatUnixTimestamp(ts).isoDate} {formatUnixTimestamp(ts).time}</p>
            {/await}
        </div>
        <div class="flex flex-col justify-center items-center">
            <p>FFT</p>
            <FFTRendering
                    showAxis
                    showYAxis
                    frequencies={fingerprint.feature_descriptors.fft.f}
                    power={fingerprint.feature_descriptors.fft.magnitudes}
                    color={colorMapping[fingerprint.label[$fingerprintMode]]}
                    width={400}
                    height={200}
            />
        </div>
        <div class="flex flex-col justify-center items-center">
            <p>Projection</p>
            <FingerprintRendering {fingerprint} {dataProvider} color={colorMapping[fingerprint.label[$fingerprintMode]]} transparent/>
        </div>
        <div class="flex flex-col justify-center items-center">
            <p>Average Cluster FFT</p>
            <FFTRendering
                    showAxis
                    showYAxis
                    frequencies={fingerprint.feature_descriptors.fft.f}
                    power={averageFFT}
                    color={colorMapping[fingerprint.label[$fingerprintMode]]}
                    width={400}
                    height={200}
            />
        </div>
    </div>

</div>
