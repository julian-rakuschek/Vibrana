import type {ScatterPoint} from "@lib/types";
import {DummyClusterRBush} from "@lib/helper/brushHelper";

type IndexRequirement = {
    index: number;
}

class DBSCAN<DataType extends IndexRequirement> {
    protected readonly eps: number;
    protected readonly minPts: number;
    protected data: DataType[];
    protected labels: number[];
    protected cluster_id_count: number;

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

    neighborhoodQuery(query: DataType): DataType[] {
        return [];
    }

    cluster() {
        this.cluster_id_count = 0;
        this.labels = Array(this.data.length).fill(undefined)

        for (let i = 0; i < this.data.length; i++) {
            if (this.labels[i]) continue;
            let seeds = this.neighborhoodQuery(this.data[i]);
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
        return this.labels;
    }

    insert(new_point: DataType) {
        this.data.push(new_point);
    }
}


export class DBSCAN_Scatter extends DBSCAN<ScatterPoint>{
    private rbush: DummyClusterRBush;

    constructor(eps: number, minPts: number, data: ScatterPoint[]) {
        super(eps, minPts, data);
        this.rbush = new DummyClusterRBush()
        this.rbush.load(data);
    }

    reset() {
        super.reset();
        this.rbush.clear();
    }

    neighborhoodQuery(query: ScatterPoint): ScatterPoint[] {
        return this.rbush.find(query.x, query.y, this.eps);
    }

    insert(new_point: ScatterPoint) {
        this.rbush.insert(new_point);
        super.insert(new_point);
    }
} 