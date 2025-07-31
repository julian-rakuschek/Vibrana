<script lang="ts">
    import ClusterOverviewBackground
        from "@components/dataset-analysis/large-signal-pda/overview/ClusterOverviewBackground.svelte";
    import type {Fingerprint} from "@lib/types.js";
    import type {ClusterColorMapping} from "@lib/types.js";
    import type {DataProvider} from "@lib/dataProvider/dataProvider.js";
    import ClusterOverviewRepresentatives
        from "@components/dataset-analysis/large-signal-pda/overview/ClusterOverviewRepresentatives.svelte";

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[] = [];
    export let colorMapping: ClusterColorMapping;
    export let dataProvider: DataProvider;
    export let width: number = 1000;
</script>

<div class="w-full relative h-[100px]">
    <div class="w-full absolute top-0 left-0">
        <ClusterOverviewBackground {width} {dataset} {subset} {fingerprints} {dataProvider} {colorMapping}/>
    </div>
    <div class="w-full absolute top-0 left-0">
        <ClusterOverviewRepresentatives {width} {dataset} {subset} {fingerprints} {dataProvider} {colorMapping}/>
    </div>
</div>