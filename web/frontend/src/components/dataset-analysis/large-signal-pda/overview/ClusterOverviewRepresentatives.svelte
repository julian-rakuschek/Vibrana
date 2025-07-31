<script lang="ts">
    import type {ClusterColorMapping, ClusterOverviewSector, Fingerprint} from '@lib/types';
    import {onMount} from 'svelte';
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {computeIndexAllocationArray} from "@lib/helper/fingerprintHelper";
    import {fillGaps} from "@lib/algorithms/gapFill";

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[] = [];
    export let colorMapping: ClusterColorMapping;
    export let dataProvider: DataProvider;
    let loading = dataProvider.loading;

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 1000;
    const height = 100;
    let labelAllocation: number[] = [];
    let indexAllocation: number[] = [];

    export function visualizeFingerprint(fp: Fingerprint, x_offset: number, color: string) {
		const projected = dataProvider.get_fingerprint_data_javascript(fp);

		const min_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[0];
		const max_x_value = projected.map(d => d[0]).toSorted((a, b) => a - b)[projected.length - 1];
		const min_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[0];
		const max_y_value = projected.map(d => d[1]).toSorted((a, b) => a - b)[projected.length - 1];

		if (!context) return;

		for (let i = 0; i < projected.length; i++) {
			const x = (projected[i][0] - min_x_value) / (max_x_value - min_x_value);
			const y = (projected[i][1] - min_y_value) / (max_y_value - min_y_value);
            context.fillStyle = color;
			context.fillRect(x * height + x_offset, y * height, 1, 1);
		}
	}

    function getSectors() {
        const filledGaps = fillGaps(labelAllocation, null);
        if (filledGaps[0] === null) return [];
        const sectors: ClusterOverviewSector[] = [];
        let currentSector: ClusterOverviewSector = {fingerprintIndices: new Set(), indices: [], clusterLabel: filledGaps[0]}
        for (let i = 0; i < width; i++) {
            const label = filledGaps[i];
            if (label !== currentSector.clusterLabel) {
                sectors.push(currentSector);
                currentSector = {fingerprintIndices: new Set(), indices: [], clusterLabel: label};
            }
            currentSector.indices.push(i);
            if (indexAllocation[i] !== -1) currentSector.fingerprintIndices.add(indexAllocation[i]);
        }
        sectors.push(currentSector);
        return sectors;
    }

    function render() {
        if (!context) return;
        context.clearRect(0, 0, width, height);
        const sectors = getSectors();
        for (const sector of sectors) {
            const maxFingerprints = Math.floor(sector.indices.length / height);
            for (let i = 0; i < maxFingerprints; i++) {
                if (i >= sector.fingerprintIndices.size) break;
                const index = Math.floor(sector.fingerprintIndices.size / maxFingerprints * i);
                const fpIndices = sector.fingerprintIndices.values().toArray()
                const fingerprint = fingerprints[fpIndices[index]];
                const x_offset = sector.indices[0] + i * height;
                visualizeFingerprint(fingerprint, x_offset, colorMapping[fingerprint.label])
            }
        }


    }

    function updateProcedure(fingerprints: Fingerprint[]) {
        indexAllocation = computeIndexAllocationArray(fingerprints, width, -1, false);
        labelAllocation = computeIndexAllocationArray(fingerprints, width, null, true);
        render();
    }

    onMount(async () => {
        context = canvas.getContext('2d');
        updateProcedure(fingerprints)
    })

    loading.subscribe(() => {
        updateProcedure(fingerprints)
    })

    $: {
        updateProcedure(fingerprints)
    }
</script>

<div class="w-full">
    <canvas {height} {width} bind:this={canvas}></canvas>
</div>