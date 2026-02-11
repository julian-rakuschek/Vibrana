import {writable} from 'svelte/store';

export const fingerprintMode = writable<"tde" | "psd">("tde");