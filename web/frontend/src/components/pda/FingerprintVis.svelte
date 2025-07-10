<script lang="ts">
    import type {HyperplaneVector} from "@lib/types";
    import {onMount} from "svelte";
    import { page } from '$app/stores';
    import {DataProvider} from "@lib/dataProvider/dataProvider";

    export let dataset: string;
    export let subset: string;

    let dataProvider: DataProvider;

    onMount(async () => {
        console.log($page.data.config)
        dataProvider = new DataProvider(
            dataset, subset,
            $page.data.config[dataset][subset].sliding_window_size,
            $page.data.config[dataset].in_memory
        )
        await dataProvider.wasm_load();
    })

</script>