import type {ClusterHistogram, HyperplaneVector, ScatterPoint} from '@lib/types';
import {DummyClusterRBush} from '@lib/helper/brushHelper';
import {createColorsArray} from '@lib/helper/colorHelper';
import { interpolateRainbow, interpolateSinebow, interpolateTurbo } from 'd3';
import {jensenShannon} from "@lib/algorithms/jensenShannonDivergence";

type IndexRequirement = {
	index: number;
}

class DBSCAN<DataType extends IndexRequirement> {
	protected readonly eps: number;
	protected readonly minPts: number;
	protected data: DataType[];
	protected labels: number[];
	protected cluster_id_count: number;
	protected colors: { [key: number]: string } = {};
	protected color_stops: number[] = [0];

	constructor(eps: number, minPts: number, data: DataType[]) {
		this.eps = eps;
		this.minPts = minPts;
		this.data = data;
		this.cluster_id_count = 0;
		this.labels = [];
	}

	reset() {
		this.data = [];
		this.labels = [];
		this.cluster_id_count = 0;
	}

	getColor(index: number): string {
		if (index === undefined || index >= this.labels.length || this.labels[index] === undefined) return 'lightgray';
		if (this.labels[index] === -1) return "gray";
		if (!this.colors[this.labels[index]]) {
			let color_stop = 0
			if (this.color_stops.length === 1) color_stop = 1;
			else if (this.color_stops.length > 1) {
				let max_diff = 0;
				let current_min_diff_pair: [number, number] | null = null;
				for (let i = 0; i < this.color_stops.length - 1; i++) {
					const diff = this.color_stops[i + 1] - this.color_stops[i];
					if (diff > max_diff || current_min_diff_pair === null) {
						max_diff = diff;
						current_min_diff_pair = [this.color_stops[i], this.color_stops[i + 1]];
					}
				}
				if (current_min_diff_pair) color_stop = (current_min_diff_pair[0] + current_min_diff_pair[1]) / 2;
			}
			console.log(color_stop);
			this.color_stops.push(color_stop);
			this.color_stops.sort();
			console.log(this.color_stops);
			this.colors[this.labels[index]] = interpolateSinebow(color_stop);
		}
		return this.colors[this.labels[index]];
	}

	getAllColors(): string[] {
		return this.labels.map(l => this.getColor(l));
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

	insert(new_point: DataType): number {
		this.data.push(new_point);
		const [new_cores, old_cores] = this.separate_core_neighbors_by_novelty(new_point);

		const update_seeds = this.get_update_seeds(new_cores);
		const update_labels = Array.from(new Set(update_seeds.map(item => this.labels[item.index]))).filter(i => i !== undefined);
		update_labels.sort();

		// console.log("new cores", new_cores);
		// console.log("old cores", old_cores);
		// console.log("update_seeds", update_seeds);
		// console.log("update_labels", update_labels);
		let changes_count = 0;
		// Case (1) Noise
		if (update_seeds.length === 0) {
			// console.log("CASE Noise")
			this.labels.push(-1);
			changes_count++;
		}
		// Case (2) Creation
		else if (update_labels.length === 1 && update_labels[0] === -1) {
			// console.log("CASE Creation")
			const new_cluster_id = this.cluster_id_count;
			this.cluster_id_count++;
			this.labels.push(new_cluster_id);
			changes_count++;
			for (const seed of update_seeds) {
				if (this.labels[seed.index] !== new_cluster_id) changes_count++;
				this.labels[seed.index] = new_cluster_id;
			}
		}
		// Case (3) Absorption and Case (4) Merge
		else {
			// console.log("CASE Absorption and Merge")
			const last_label = update_labels[update_labels.length - 1];
			this.labels.push(last_label);
			changes_count++;
			for (const seed of update_seeds) {
				if (this.labels[seed.index] !== last_label) changes_count++;
				this.labels[seed.index] = last_label;
			}
			const upd_labels_no_noise = update_labels.filter(i => i !== -1);
			if (upd_labels_no_noise.length >= 2) {
				for (let i = 0; i < this.labels.length; i++) {
					if (upd_labels_no_noise.includes(this.labels[i])) {
						if (this.labels[i] !== last_label) changes_count++;
						this.labels[i] = last_label;
					}
				}
			}
		}
		return changes_count;
	}

	separate_core_neighbors_by_novelty(point_inserted: DataType): [DataType[], DataType[]] {
		const new_cores: DataType[] = [];
		const old_cores: DataType[] = [];
		const neighbors = this.neighborhoodQuery(point_inserted);
		if (neighbors.length >= this.minPts) new_cores.push(point_inserted);

		for (const neighbor of neighbors) {
			const neighbor_neighbors = this.neighborhoodQuery(neighbor);
			if (neighbor.index === point_inserted.index) continue;
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

	get_cluster_distribution(): ClusterHistogram {
		const hist: { [key: string]: number } = {"-1": 0}
		for (const label of this.labels) {
			if (!hist[label]) hist[label] = 0;
			hist[label]++;
		}
		return Object.keys(hist).map(cluster_id => ({
			cluster_id: cluster_id,
			size: hist[cluster_id],
			color: cluster_id === "-1" ? "gray" : this.colors[Number.parseInt(cluster_id)],
			relative_size: hist[cluster_id] / this.labels.length
		}));
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

	insert(new_point: ScatterPoint): number {
		this.rbush.insert(new_point);
		return super.insert(new_point);
	}
}

export class DBSCAN_VibrationFingerprints extends DBSCAN<HyperplaneVector> {
	private similarity_matrix: Float32Array = new Float32Array(1000);

	constructor(eps: number, minPts: number, data: HyperplaneVector[]) {
		super(eps, minPts, data);
		this.compute_similarity_matrix();
	}

	resizeFloat32Array(new_size: number) {
		if (new_size < this.similarity_matrix.length) throw "New size needs to be larger or equal than old size";
		const newArray = new Float32Array(new_size);
		newArray.set(this.similarity_matrix);
		this.similarity_matrix = newArray;
	}

	compute_similarity_matrix() {
		const N = this.data.length;
		const required_slots = (N*N - N) / 2;
		if (required_slots > this.similarity_matrix.length) this.resizeFloat32Array(required_slots);
		let index_count = 0;
		for (let i = 0; i < N; i++) {
			for (let j = 0; j < N; j++) {
				if (i == j) break;
				const q = this.data[i].feature_descriptors.radii_distribution.counts;
				const p = this.data[j].feature_descriptors.radii_distribution.counts;
				this.similarity_matrix[index_count] = jensenShannon(p, q);
				index_count++;
			}
		}
	}

	access_similarity_entry(i: number, j: number): number {
		if (j > i) [i, j] = [j, i];
		if (i === j) return 0;
		const flat_index = (i*(i-1)) / 2 + j;
		return this.similarity_matrix[flat_index];
	}
	
	get_full_similarity_matrix(): number[][] {
		const mat: number[][] = [];
		for (let i = 0; i < this.data.length; i++) {
			const row: number[] = [];
			for (let j = 0; j < this.data.length; j++) {
				row.push(this.access_similarity_entry(i, j))
			}
			mat.push(row)
		}
		return mat;
	}

	neighborhoodQuery(query: HyperplaneVector): HyperplaneVector[] {
		const neighbors: HyperplaneVector[] = [];
		for (let i = 0; i < this.data.length; i++) {
			if (query.index === i) continue;
			const dist = this.access_similarity_entry(query.index, i);
			if (dist < this.eps) {
				neighbors.push(this.data[i]);
			}
		}
		return neighbors;
	}

	insert(new_point: HyperplaneVector): number {
		const N = this.data.length;
		const required_slots = (N*N - N) / 2;
		if (required_slots > this.similarity_matrix.length) this.resizeFloat32Array(required_slots + 1000);
		let index = required_slots
		for (let i = 0; i < this.data.length; i++) {
			const q = this.data[i].feature_descriptors.radii_distribution.counts;
			const p = new_point.feature_descriptors.radii_distribution.counts;
			this.similarity_matrix[index] = jensenShannon(p, q);
			index++;
		}
		return super.insert(new_point);
	}
}