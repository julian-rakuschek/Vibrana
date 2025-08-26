import {type Dendrogram} from "../types";

export function getDValues(dendrogram: Dendrogram): number[] {
    let left = [] as number[];
    let right = [] as number[];

    if (dendrogram.left) {
        left = [...getDValues(dendrogram.left)];
    }
    if (dendrogram.right) {
        right = [...getDValues(dendrogram.right)];
    }
    if (dendrogram.dist) {
        return [...left, dendrogram.dist, ...right];
    } else {
        return [...left, ...right];
    }

}

export function getAllLeafs(dendrogram: Dendrogram): string[] {
    let left: string[] = [];
    let right: string[] = [];

    if (dendrogram.left) {
        left = [...getAllLeafs(dendrogram.left)];
    }
    if (dendrogram.right) {
        right = [...getAllLeafs(dendrogram.right)];
    }
    let ret: string[] = [...left, ...right];
    if (!dendrogram.left && !dendrogram.right) ret = [dendrogram.id, ...ret];
    return ret;
}

export function getClusters(dendrogram: Dendrogram, d: number): string[][] {
    if (dendrogram.dist && dendrogram.dist > d) {
        const leftNodes = dendrogram.left ? getClusters(dendrogram.left, d) : [];
        const rightNodes = dendrogram.right ? getClusters(dendrogram.right, d) : [];
        return [...leftNodes, ...rightNodes];
    } else {
        return [getAllLeafs(dendrogram)];
    }
}

export function getLeafsWithClusterLabels(dendrogram: Dendrogram, d: number): [string, number][] {
    const cluster = getClusters(dendrogram, d);
    const labels: [string, number][] = []
    for (let i = 0; i < cluster.length; i++) {
        for (let j = 0; j < cluster[i].length; j++) {
            labels.push([cluster[i][j], i])
        }
    }
    labels.sort((a, b) => {
        if (a[0] < b[0]) return -1;
        if (a[0] > b[0]) return 1;
        return 0;
    });
    return labels;
}

