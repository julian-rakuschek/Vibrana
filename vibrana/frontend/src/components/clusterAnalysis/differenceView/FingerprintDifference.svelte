<script lang="ts">
    import type {Fingerprint} from "@lib/types";
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import PSDDifference from "@components/clusterAnalysis/differenceView/PSDDifference.svelte";

    interface Props {
        fingerprint1: Fingerprint;
        fingerprint2: Fingerprint;
        averagePSD1: number[];
        averagePSD2: number[];
    }

    let {fingerprint1, fingerprint2, averagePSD1, averagePSD2}: Props = $props();

    function computePSDDelta(psd1: number[], psd2: number[]) {
        return psd1.map((power, i) => power - (psd2[i] ?? 0));
    }
</script>

<div class="flex flex-col items-center justify-between h-[90%] mt-13 w-[300px]">
    <div class="flex flex-col justify-center items-center">
        <p>Single PSD Difference</p>
        <PSDDifference
                showAxis
                size={200}
                frequencies={fingerprint1.feature_descriptors.psd.f}
                delta={computePSDDelta(fingerprint2.feature_descriptors.psd.Pxx_spec, fingerprint1.feature_descriptors.psd.Pxx_spec)}
        />
    </div>
    <div class="flex flex-col justify-center items-center">
        <p>Average PSD Difference</p>
        <PSDDifference
                showAxis
                size={200}
                frequencies={fingerprint2.feature_descriptors.psd.f}
                delta={computePSDDelta(averagePSD2, averagePSD1)}
        />
    </div>
</div>
