<script lang="ts">
    import {
        Menu,
        MenuButton,
        MenuItems,
        MenuItem, Transition,
    } from "@rgossiaux/svelte-headlessui";
    import {Icon, Wrench} from "svelte-hero-icons";
    import {ColorMode, ProjectionMode, WindowMode, type ThreeChartsSettingsType} from "@lib/types.js";
    import {chartSettings} from "@lib/stores";

    const radioSelections = [
        {
            "key": "window",
            "label": "Window Type",
            "options": [
                {"label": "Sliding Windows", "value": WindowMode.Sliding},
                {"label": "Disjoint Windows", "value": WindowMode.Disjoint},
            ],
        },
        {
            "key": "projection",
            "label": "Projection",
            "options": [
                {"label": "Time Series Paths", "value": ProjectionMode.Paths},
                {"label": "Clustering", "value": ProjectionMode.Cluster},
            ],
        },
        {
            "key": "color",
            "label": "Coloring",
            "options": [
                {"label": "Radius", "value": ColorMode.Radius},
                {"label": "Mean amplitude of the SFFT over time.", "value": ColorMode.Frequency},
                {"label": "Distance", "value": ColorMode.Distance},
            ],
        },
    ]

    const updateSettings = (category, value: WindowMode | ProjectionMode | ColorMode): void => {
        chartSettings.update(s => ({...s, [category]: value}))
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
                                        checked={$chartSettings[category.key] === option.value}
                                        type="radio"
                                        class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-offset-0 focus:ring-0"
                                        on:click={() => updateSettings(category.key, option.value)}
                                />
                                <label htmlFor={`${category.key}_${option.value}`}
                                       class="ml-3 block text-sm font-medium leading-6 text-gray-900">{option.label}</label>
                            </div>
                        {/each}
                    </fieldset>
                </div>
            {/each}
        </MenuItems>
    </Transition>
</Menu>