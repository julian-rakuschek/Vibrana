<script lang="ts">
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {onMount} from "svelte";
    import {Pulse} from "svelte-loading-spinners";


    export let dataProvider: DataProvider;
    let loading = false;

    onMount(async () => {
        if (dataProvider.isInMemory()) {
            loading = true;
            await dataProvider.load()
            loading = false;
        }
    })
</script>

{#if loading}
    <div class="bg-indigo-800 w-full rounded-lg flex flex-row gap-5 p-3 justify-center items-center">
        <Pulse color="#FFFFFF" size="30" unit="px" />
        <p class="text-white">Loading Dataset</p>
    </div>
{:else}
    <div class="bg-teal-100 w-full rounded-lg flex flex-row gap-5 p-3 justify-center items-center">
        <p class="text-teal-600">Load Complete</p>
    </div>
{/if}

