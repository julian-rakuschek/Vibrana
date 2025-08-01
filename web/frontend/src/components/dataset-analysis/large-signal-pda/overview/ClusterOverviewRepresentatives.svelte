<script lang="ts">
	import type { ClusterColorMapping, ClusterOverviewSector, Fingerprint } from '@lib/types';
	import { onMount } from 'svelte';
	import type { DataProvider } from '@lib/dataProvider/dataProvider';
	import { fillGaps } from '@lib/algorithms/gapFill';
	import FingerprintRendering from '@components/atoms/FingerprintRendering.svelte';
	import CenteredLoadingSpinner from '@components/atoms/CenteredLoadingSpinner.svelte';

	export let fingerprints: Fingerprint[] = [];
	export let colorMapping: ClusterColorMapping;
	export let dataProvider: DataProvider;
	export let label_allocation: number[] = [];
	export let index_allocation: number[] = [];
	export let width = 1000;
	let loading = dataProvider.loading;

	const height = 100;
	let chosen_fingerprints: RepresentativeFingerprints[] = [];

	type RepresentativeFingerprints = {
		fp: number;
		x_offset: number;
		label: number;
	}

	function getSectors(filledGaps: number[], index_allocation: number[]): ClusterOverviewSector[] {
		const sectors: ClusterOverviewSector[] = [];
		let currentSector: ClusterOverviewSector = { fingerprintIndices: new Set(), indices: [], clusterLabel: filledGaps[0] };
		for (let i = 0; i < width; i++) {
			const label = filledGaps[i];
			if (label !== currentSector.clusterLabel) {
				sectors.push(currentSector);
				currentSector = { fingerprintIndices: new Set(), indices: [], clusterLabel: label };
			}
			currentSector.indices.push(i);
			if (index_allocation[i] !== -1) currentSector.fingerprintIndices.add(index_allocation[i]);
		}
		sectors.push(currentSector);
		return sectors;
	}

	function getFingerprintFromSector(sector: ClusterOverviewSector, seen: number[]) {
		let sector_fingerprints = Array.from(sector.fingerprintIndices);
		sector_fingerprints = sector_fingerprints.filter(f => !seen.includes(f));
		sector_fingerprints = sector_fingerprints.toSorted((a, b) => a - b);
		return sector_fingerprints[0];
	}

	function getRepresentativeFingerprints(filledGaps: number[], sectors: ClusterOverviewSector[]): RepresentativeFingerprints[] {
		const result: RepresentativeFingerprints[] = [];
		let current_sector = 0;
		let current_label = filledGaps[0];
		let fp_width_needle = 0;
		for (let i = 0; i < width; i++) {
			if (filledGaps[i] !== current_label) {
				current_label = filledGaps[i];
				current_sector++;
				fp_width_needle = 0;
			}
			if (fp_width_needle === height) {
				const sector_fingerprint = getFingerprintFromSector(sectors[current_sector], result.map(f => f.fp));
				result.push({ fp: sector_fingerprint, label: current_label, x_offset: i - height });
				fp_width_needle = 0;
			} else {
				fp_width_needle++;
			}
		}
		return result;
	}

	function getChosenFingerprints(label_allocation: number[], index_allocation: number[]) {
		const filledGaps = fillGaps(label_allocation, null);
		if (filledGaps.includes(null)) return [];
		const sectors = getSectors(filledGaps as number[], index_allocation);
		return getRepresentativeFingerprints(filledGaps as number[], sectors);
	}

</script>

<div class="w-full relative">
	{#if $loading}
		<CenteredLoadingSpinner />
	{:else}
		{#each getChosenFingerprints(label_allocation, index_allocation) as fp}
			{#key `${fp.fp}-${fp.label}-${fp.x_offset}`}
				<div class="absolute" style={`height: ${height}px; width: ${height}px; left: ${fp.x_offset}px`}>
					<FingerprintRendering size={height} fingerprint={fingerprints[fp.fp]} dataProvider={dataProvider} transparent color={colorMapping[fp.label]} update_on_fp_change={false} />
				</div>
			{/key}
		{/each}
	{/if}
</div>