import { writable } from 'svelte/store';

export let filterRangePercent = writable<null | [number, number]>(null)
export let filterRangeIndexed = writable<null | [number, number]>(null)