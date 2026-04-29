<script lang="ts">
    import type {DataProvider} from "@lib/dataProvider/dataProvider";
    import {onMount} from "svelte";
    import {Pulse} from "svelte-loading-spinners";

    interface Props {
        dataProvider: DataProvider;
    }

    let {dataProvider}: Props = $props();
    let loading = $derived(dataProvider.loading);

    onMount(async () => {
        await dataProvider.load()
    })
</script>

{#if $loading}
    <div class="bg-indigo-800 w-full rounded-lg flex flex-row gap-5 p-3 justify-center items-center">
        <Pulse color="#FFFFFF" size="30" unit="px"/>
        <p class="text-white">Loading Dataset</p>
    </div>
{:else}
    {#if dataProvider.isInMemory()}
        <div class="bg-teal-100 w-full rounded-lg flex flex-col p-3 justify-center items-center">
            <p class="text-teal-600 text-sm">The signal has been loaded into browser memory
                with {dataProvider.get_length().toLocaleString()} data points.</p>
        </div>
    {:else}
        <div class="bg-teal-100 w-full rounded-lg flex flex-col p-3 justify-center items-center">
            <p class="text-teal-600 text-sm">The signal is not in memory, slices will be fetched on demand.</p>
        </div>
    {/if}
{/if}

