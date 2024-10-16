<script lang="ts">
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import QueryWrapper from "@lib/api/QueryWrapper.svelte";
    import {Dialog, DialogOverlay, Transition, TransitionChild} from "@rgossiaux/svelte-headlessui";
    import {useQueryClient} from "@tanstack/svelte-query";

    const machineListQuery = useQueryFetch(ApiRoutes.getMachinesList)
    const queryClient = useQueryClient();

    let isOpen = false;
    let machine_name: string = "";

    const save = async () => {
        await ApiRoutes.addMachine.fetch({data: {machineName: machine_name}})
        await queryClient.invalidateQueries()
        isOpen = false;
        machine_name = ""
    }
</script>

<p class="text-center text-xl font-semibold">Available Machines</p>
<QueryWrapper query={machineListQuery}>
    {#if $machineListQuery.data}
        <div class="flex flex-col p-10 w-full items-center gap-5">
            {#each $machineListQuery.data as machine}
                <a
                        href={`/machines/${machine}/analyze`}
                        class="w-[300px] h-[40px] shadow-md rounded-lg flex flex-row justify-around items-center transition hover:shadow-lg"
                >
                    <span class="font-semibold">{machine}</span>
                </a>
            {/each}
            <button on:click={() => isOpen = true} class="w-[300px] h-[40px] bg-indigo-500 cursor-default text-white shadow-md rounded-lg flex flex-row justify-around items-center transition hover:shadow-lg hover:bg-indigo-700">
                Add Machine
            </button>
        </div>
    {/if}
</QueryWrapper>

<Transition show={isOpen}>
    <Dialog open={isOpen} on:close={() => (isOpen = false)} class="z-10 fixed top-0 left-0 flex justify-center items-center w-full h-full">
        <TransitionChild
                enter="ease-out duration-300"
                enterFrom="opacity-0"
                enterTo="opacity-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
        >
            <DialogOverlay class="fixed top-0 left-0 bg-black/30 w-full h-full"/>
        </TransitionChild>
        <div class="z-10">
             <TransitionChild
                enter="ease-out duration-200"
                enterFrom="opacity-0 scale-75"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-100"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-100"
        >
            <div class="bg-white rounded-lg p-4 flex flex-col items-center gap-4">
                <p class="text-lg font-semibold">Add Machine</p>
                <input bind:value={machine_name} placeholder="Machine Name" class="block w-full rounded-md border-0 py-1.5 pl-7 pr-20 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                <button on:click={save} class="bg-indigo-500 text-white hover:bg-indigo-700 transition px-2 py-1 rounded-md">Add</button>
            </div>
        </TransitionChild>
        </div>

    </Dialog>
</Transition>

