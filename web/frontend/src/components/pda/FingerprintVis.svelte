<script lang="ts">
    import type {HyperplaneVector} from "@lib/types";
    import {onMount} from "svelte";
    import { page } from '$app/stores';

    export let dataset: string;
    export let subset: string;

    onMount(() => {
        console.log($page.data.config)
    })

</script>