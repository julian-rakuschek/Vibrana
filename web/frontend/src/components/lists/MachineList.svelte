<script lang="ts">
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import QueryWrapper from "@lib/api/QueryWrapper.svelte";

    const machineListQuery = useQueryFetch(ApiRoutes.getMachinesList)
</script>

<QueryWrapper query={machineListQuery}>
    {#if $machineListQuery.data}
        <div class="flex flex-row p-10">
            {#each $machineListQuery.data as machine}
                <a
                        href={`/machines/${machine}/analyze`}
                        class="w-[300px] h-[40px] shadow-lg rounded-lg flex flex-row justify-around items-center transition hover:shadow-xl"
                >
                    <span class="font-semibold">{machine}</span>
                    <div class="rounded-full w-[15px] h-[15px] bg-green-500"></div>
                </a>
            {/each}
        </div>
    {/if}
</QueryWrapper>

