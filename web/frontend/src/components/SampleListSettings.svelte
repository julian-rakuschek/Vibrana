<script lang="ts">
    import {type SamplesSettingsType, SortMode} from "@lib/types";
    import {
        Menu,
        MenuButton,
        MenuItems,
        MenuItem, Transition,
    } from "@rgossiaux/svelte-headlessui";
    import {Icon, Wrench} from "svelte-hero-icons";
    import Toggle from "@components/atoms/Toggle.svelte";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {useQueryClient} from "@tanstack/svelte-query";

    export let settings: SamplesSettingsType;
    export let machine: string;

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

    const reset = async () => {
        await ApiRoutes.reset.fetch({params: {machineId: machine}});
        await client.invalidateQueries()
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
            <div class="flex flex-col">
                <label class="text-base font-semibold text-gray-900">Split by Ground Truth</label>
                <Toggle bind:enabled={settings.split}/>
            </div>
            <button class="text-sm text-red-500 bg-red-300/50 rounded-lg transition hover:bg-red-500 hover:text-white" on:click={() => reset()}>Reset Labels</button>
        </MenuItems>
    </Transition>
</Menu>