<script lang="ts">
    import type {Fingerprint} from "@lib/types";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import FFTDifference from "@components/clusterAnalysis/differenceView/FFTDifference.svelte";

    interface Props {
        fingerprint1: Fingerprint;
        fingerprint2: Fingerprint;
        averageFFT1: number[];
        averageFFT2: number[];
    }

    let {fingerprint1, fingerprint2, averageFFT1, averageFFT2}: Props = $props();

    function computeFFTDelta(fft1: number[], fft2: number[]) {
        return fft1.map((power, i) => power - (fft2[i] ?? 0));
    }
</script>

<div class="flex flex-col items-center justify-between h-[90%] mt-13 w-[300px]">
    <div class="flex flex-col justify-center items-center">
        <p>Single FFT Difference</p>
        <FFTDifference
                showAxis
                size={200}
                frequencies={fingerprint1.feature_descriptors.fft.f}
                delta={computeFFTDelta(fingerprint2.feature_descriptors.fft.magnitudes, fingerprint1.feature_descriptors.fft.magnitudes)}
        />
    </div>
    <div class="flex flex-col justify-center items-center">
        <p>Average FFT Difference</p>
        <FFTDifference
                showAxis
                size={200}
                frequencies={fingerprint2.feature_descriptors.fft.f}
                delta={computeFFTDelta(averageFFT2, averageFFT1)}
        />
    </div>
</div>
