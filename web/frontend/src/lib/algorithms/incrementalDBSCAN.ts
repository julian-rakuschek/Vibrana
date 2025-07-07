type IndexRequirement = {
    index: number;
}

export function DBSCAN<DataType extends IndexRequirement>(
    data: DataType[],
    neighborhood_query: (query: DataType, eps: number) => DataType[],
    minPoints: number,
    eps: number
): number[] {
    let cluster_id_count = 0;

    const labels: number[] = Array(data.length).fill(undefined)
    for (let i = 0; i < data.length; i++) {
        if (labels[i]) continue;
        let seeds = neighborhood_query(data[i], eps);
        if (seeds.length < minPoints) {
            labels[i] = -1;
            continue;
        }
        const new_cluster_id = cluster_id_count;
        cluster_id_count++;
        while (seeds.length > 0) {
            const current_object = seeds.pop();
            if (!current_object) break;
            const N = neighborhood_query(current_object, eps);
            if (N.length >= minPoints) {
                for (const nElement of N) {
                    if (labels[nElement.index] === undefined || labels[nElement.index] === -1) {
                        labels[nElement.index] = new_cluster_id;
                        seeds.push(nElement);
                    }
                }
            }
        }
    }
    return labels;
}