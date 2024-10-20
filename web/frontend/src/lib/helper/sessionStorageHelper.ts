import type {AnalysisPostData, Label, LabelBase} from "@lib/types";
import { v4 as uuidv4 } from 'uuid';

export const sessionGetNormals = (machine: string): string[] => {
    const normals: { [machine: string]: string[] } = JSON.parse(localStorage.getItem("normals") ?? "{}")
    return normals[machine] ?? []
}

export const sessionToggleNormal = (machine: string, sample: string) => {
    const normals: { [machine: string]: string[] } = JSON.parse(localStorage.getItem("normals") ?? "{}")
    let samples = normals[machine] ?? []
    if (samples.indexOf(sample) !== -1) samples = samples.filter(s => s !== sample)
    else samples.push(sample)
    normals[machine] = samples
    localStorage.setItem("normals", JSON.stringify(normals))
}

export const sessionGetLabels = (machine: string, sample?: string): Label[] => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l.machine === machine)
    if (sample) {
        labels = labels.filter(l => l.sampleId === sample)
    }
    return labels
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

export const sessionDeleteLabelPyPos = (machine: string, sample: string, pos: number) => {
    let labels: Label[] = JSON.parse(localStorage.getItem("labels") ?? "[]")
    labels = labels.filter(l => l.machine !== machine || l.sampleId !== sample || !(l.from <= pos && pos <= l.to))
    localStorage.setItem("labels", JSON.stringify(labels))
}

export const sessionGetAll = (machine: string): AnalysisPostData => {
    const samples = sessionGetNormals(machine)
    const labels = sessionGetLabels(machine)
    return {
        normals: {machine, samples},
        labels: labels
    }
}

export const itemSeen = (machine: string, sample: string): boolean => {
    const viewHistory: string[] = JSON.parse(localStorage.getItem("viewHistory") ?? "[]")
    return viewHistory.indexOf(`${machine}-${sample}`) !== -1
}

export const setItemSeen = (machine: string, sample: string) => {
    const viewHistory: string[] = JSON.parse(localStorage.getItem("viewHistory") ?? "[]")
    viewHistory.push(`${machine}-${sample}`)
    localStorage.setItem("viewHistory", JSON.stringify(viewHistory))
}