import type {AnalysisPostData, Label, LabelBase, LabelCount, SessionNormals} from "@lib/types";
import {v4 as uuidv4} from 'uuid';

export const sessionGetNormals = (dataset: string, subset: string): string[] => {
    const normals: SessionNormals = JSON.parse(localStorage.getItem("normals") ?? "{}")
    if (!normals[dataset]) return []
    return normals[dataset][subset] ?? []
}

export const sessionToggleNormal = (dataset: string, subset: string, chunk: string) => {
    const normals: SessionNormals = JSON.parse(localStorage.getItem("normals") ?? "{}")
    if (!normals[dataset]) normals[dataset] = {}
    let chunks = normals[dataset][subset] ?? []
    if (chunks.indexOf(chunk) !== -1) chunks = chunks.filter(c => c !== chunk)
    else chunks.push(chunk)
    normals[dataset][subset] = chunks
    localStorage.setItem("normals", JSON.stringify(normals))
}

export const sessionGetLabels = (dataset: string, subset: string, chunk?: string): Label[] => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l.dataset === dataset)
    labels = labels.filter(l => l.subset === subset)
    if (chunk) {
        labels = labels.filter(l => l.chunk === chunk)
    }
    return labels
}

export const sessionGetLabelCount = (dataset: string, subset: string): LabelCount[] => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l.dataset === dataset)
    labels = labels.filter(l => l.subset === subset)
    const label_count: { [chunk: string]: number } = {}
    for (const label of labels) {
        if (!label_count[label.chunk]) label_count[label.chunk] = 0
        label_count[label.chunk]++;
    }
    return Object.keys(label_count).map(c => ({_id: c, count: label_count[c]}))
}

export const sessionAddLabel = (label: LabelBase) => {
    const label_id = uuidv4()
    const labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels.push({...label, _id: {$oid: label_id}})
    localStorage.setItem("labels", JSON.stringify(labels))
}

export const sessionDeleteLabelPyID = (labelId: string) => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l._id.$oid !== labelId)
    localStorage.setItem("labels", JSON.stringify(labels))
}

export const sessionDeleteLabelPyPos = (dataset: string, subset: string, chunk: string, pos: number) => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l.dataset !== dataset || l.subset !== subset  || l.chunk !== chunk || !(l.from <= pos && pos <= l.to))
    localStorage.setItem("labels", JSON.stringify(labels))
}

export const sessionGetAll = (dataset: string, subset: string): AnalysisPostData => {
    const chunks = sessionGetNormals(dataset, subset)
    const labels = sessionGetLabels(dataset, subset)
    return {
        normals: {dataset, subset, chunks},
        labels: labels
    }
}

export const itemSeen = (dataset: string, subset: string, chunk: string): boolean => {
    const viewHistory: string[] = JSON.parse(localStorage.getItem("viewHistory") ?? "[]")
    return viewHistory.indexOf(`${dataset}-${subset}-${chunk}`) !== -1
}

export const setItemSeen = (dataset: string, subset: string, chunk: string) => {
    const viewHistory: string[] = JSON.parse(localStorage.getItem("viewHistory") ?? "[]")
    viewHistory.push(`${dataset}-${subset}-${chunk}`)
    localStorage.setItem("viewHistory", JSON.stringify(viewHistory))
}

export const sessionResetLabels = () => {
    localStorage.setItem("normals", "{}")
    localStorage.setItem("labels", "[]")
}

export const sessionResetChunk = (dataset: string, subset: string, chunk: string) => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l.dataset !== dataset || l.subset !== subset  || l.chunk !== chunk)
    localStorage.setItem("labels", JSON.stringify(labels))
}

export const resetViewHistory = () => {
    localStorage.setItem("viewHistory", "[]")
}