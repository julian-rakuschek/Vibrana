<script lang="ts">
    import {type ChunkListSettingsType, SortMode} from "@lib/types";
    import {Menu, MenuButton, MenuItems, Transition,} from "@rgossiaux/svelte-headlessui";
    import {Icon, Wrench} from "svelte-hero-icons";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {useQueryClient} from "@tanstack/svelte-query";
    import {getContext} from "svelte";
    import {sessionResetLabels, resetViewHistory} from "@lib/helper/sessionStorageHelper";

    export let settings: ChunkListSettingsType;
    export let dataset: string;
    export let subset: string;

    const radioSelections = [
        {
            "key": "sort",
            "label": "Sort By",
            "options": [
                {"label": "Name", "value": SortMode.Name},
                {"label": "Score", "value": SortMode.Score},
            ],
        },
    ]

    const client = useQueryClient()
    const {ro} = getContext("ro") as { ro: boolean }

    const reset_labels = async () => {
        if (ro) {
            sessionResetLabels()
        } else {
            await ApiRoutes.reset.fetch({params: {dataset, subset}});
        }
        await client.invalidateQueries()
    }

    const reset_views = async () => {
        resetViewHistory()
    }


</script>

<Menu class="flex flex-col justify-end items-end">
    <MenuButton class="shadow-lg rounded-full bg-white px-2 py-2 w-10 h-10 flex justify-center items-center">
        <Icon src="{Wrench}" solid class="w-7 h-7 text-gray-700"/>
    </MenuButton>
    <Transition
            enter="transition duration-100 ease-out"
            enterFrom="transform scale-75 opacity-0"
            enterTo="transform scale-100 opacity-100"
            leave="transition duration-75 ease-out"
            leaveFrom="transform scale-100 opacity-100"
            leaveTo="transform scale-75 opacity-0"
    >
        <MenuItems class="bg-white rounded-xl p-3 mt-2 flex flex-col gap-y-3 shadow-lg">
            {#each radioSelections as category}
                <div>
                    <label class="text-base font-semibold text-gray-900">{category.label}</label>
                    <fieldset>
                        {#each category.options as option}
                            <div class="flex items-center">
                                <input
                                        id={`${category.key}_${option.value}`}
                                        name={category.key}
                                        checked={settings[category.key] === option.value}
                                        type="radio"
                                        class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-offset-0 focus:ring-0"
                                        on:click={() => settings[category.key] = option.value}
                                />
                                <label htmlFor={`${category.key}_${option.value}`}
                                       class="ml-3 block text-sm font-medium leading-6 text-gray-900">{option.label}</label>
                            </div>
                        {/each}
                    </fieldset>
                </div>
            {/each}
            <button class="text-sm text-red-500 px-3 bg-red-300/50 rounded-lg transition hover:bg-red-500 hover:text-white" on:click={() => reset_labels()}>Reset Labels</button>
            <button class="text-sm text-red-500 px-3 bg-red-300/50 rounded-lg transition hover:bg-red-500 hover:text-white" on:click={() => reset_views()}>Reset View History</button>
        </MenuItems>
    </Transition>
</Menu>