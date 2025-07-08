import type { ScatterPoint } from '@lib/types';
import { DummyClusterRBush } from '@lib/helper/brushHelper';
import { createColorsArray } from '@lib/helper/colorHelper';
import { interpolateTurbo } from 'd3';

type IndexRequirement = {
	index: number;
}

class DBSCAN<DataType extends IndexRequirement> {
	protected readonly eps: number;
	protected readonly minPts: number;
	protected data: DataType[];
	protected labels: number[];
	protected cluster_id_count: number;
	protected colors: string[];

	constructor(eps: number, minPts: number, data: DataType[]) {
		this.eps = eps;
		this.minPts = minPts;
		this.data = data;
		this.cluster_id_count = 0;
		this.labels = [];
		this.colors = createColorsArray(10, { start: 0, end: 1, reverse: false, interpolateFunc: interpolateTurbo })
	}

	reset() {
		this.data = [];
		this.labels = [];
		this.cluster_id_count = 0;
	}

	getColor(index: number): string {
		if (index === undefined || index >= this.labels.length || this.labels[index] === undefined) return 'lightgray';
		return this.colors[this.labels[index] % this.colors.length];
	}

	neighborhoodQuery(query: DataType): DataType[] {
		return [];
	}

	cluster() {
		this.cluster_id_count = 0;
		this.labels = Array(this.data.length).fill(undefined);

		for (let i = 0; i < this.data.length; i++) {
			if (this.labels[i]) continue;
			const seeds = this.neighborhoodQuery(this.data[i]);
			if (seeds.length < this.minPts) {
				this.labels[i] = -1;
				continue;
			}
			const new_cluster_id = this.cluster_id_count;
			this.cluster_id_count++;

			while (seeds.length > 0) {
				const current_object = seeds.pop();
				if (!current_object) break;
				const N = this.neighborhoodQuery(current_object);
				if (N.length >= this.minPts) {
					for (const nElement of N) {
						if (this.labels[nElement.index] === undefined || this.labels[nElement.index] === -1) {
							this.labels[nElement.index] = new_cluster_id;
							seeds.push(nElement);
						}
					}
				}
			}
		}

		const distinct_labels = Array.from(new Set(this.labels)).toSorted();
		for (let i = 0; i < this.labels.length; i++) {
			this.labels[i] = distinct_labels.indexOf(this.labels[i]);
		}
		return this.labels;
	}

	// https://github.com/DataOmbudsman/incdbscan/blob/master/incdbscan/_inserter.py
	insert(new_point: DataType) {
		this.data.push(new_point);
		const [new_cores, old_cores] = this.separate_core_neighbors_by_novelty(new_point);
		// Case (1) Noise
		// if (new_cores.length === 0) {
		//     if (old_cores.length > 0) {
		//         const most_recent_label = Math.max(...old_cores.map(c => this.labels[c.index]))
		//         this.labels.push(most_recent_label)
		//     }
		//     else {
		//         this.labels.push(-1);
		//     }
		//     return;
		// }

		const update_seeds = this.get_update_seeds(new_cores);
		const update_labels = Array.from(new Set(update_seeds.map(item => this.labels[item.index])));
		update_labels.sort();
		// Case (1) Noise
		if (update_seeds.length === 0) {
			this.labels.push(-1);
		}
		// Case (2) Creation
		else if (update_labels.length === 1 && update_labels[0] === -1) {
			const new_cluster_id = this.cluster_id_count;
			this.cluster_id_count++;
			this.labels.push(new_cluster_id);
			for (const seed of update_seeds) {
				this.labels[seed.index] = new_cluster_id;
			}
		}
		// Case (3) Absorption and Case (4) Merge
		else {
			const last_label = update_labels[update_labels.length - 1];
			this.labels.push(last_label);
			for (const seed of update_seeds) {
				this.labels[seed.index] = last_label;
			}
			const upd_labels_no_noise = update_labels.filter(i => i !== -1);
			if (upd_labels_no_noise.length >= 2) {
				for (let i = 0; i < this.labels.length; i++) {
					if (upd_labels_no_noise.includes(this.labels[i])) this.labels[i] = last_label;
				}
			}
		}
	}

	separate_core_neighbors_by_novelty(point_inserted: DataType): [DataType[], DataType[]] {
		const new_cores: DataType[] = [];
		const old_cores: DataType[] = [];
		const neighbors = this.neighborhoodQuery(point_inserted);
		for (const neighbor of neighbors) {
			const neighbor_neighbors = this.neighborhoodQuery(neighbor);
			if (neighbor.index === point_inserted.index && neighbor_neighbors.length >= this.minPts) new_cores.push(neighbor);
			else if (neighbor_neighbors.length === this.minPts) new_cores.push(neighbor);
			else if (neighbor_neighbors.length > this.minPts) old_cores.push(neighbor);
		}
		return [new_cores, old_cores];
	}

	get_update_seeds(new_cores: DataType[]) {
		const seeds: DataType[] = [];
		for (const new_core of new_cores) {
			const core_neighbors = this.neighborhoodQuery(new_core);
			for (const coreNeighbor of core_neighbors) {
				const coreNeighbor_neighbors = this.neighborhoodQuery(coreNeighbor);
				if (coreNeighbor_neighbors.length < this.minPts) continue;
				if (seeds.find(n => n.index === coreNeighbor.index)) continue;
				seeds.push(coreNeighbor);
			}
		}
		return seeds;
	}
}


export class DBSCAN_Scatter extends DBSCAN<ScatterPoint> {
	private rbush: DummyClusterRBush;

	constructor(eps: number, minPts: number, data: ScatterPoint[]) {
		super(eps, minPts, data);
		this.rbush = new DummyClusterRBush();
		this.rbush.load(data);
	}

	reset() {
		this.rbush.clear();
		super.reset();
	}

	neighborhoodQuery(query: ScatterPoint): ScatterPoint[] {
		return this.rbush.find(query.x, query.y, this.eps);
	}

	insert(new_point: ScatterPoint) {
		this.rbush.insert(new_point);
		super.insert(new_point);
	}
} 