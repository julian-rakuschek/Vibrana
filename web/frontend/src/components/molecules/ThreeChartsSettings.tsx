import {Fragment, ReactElement} from "react";
import {Menu, Transition} from "@headlessui/react";
import {WrenchIcon} from "@heroicons/react/24/solid";
import {ColorMode, ProjectionMode, ThreeChartsSettingsType, WindowMode} from "../../types";

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
            {"label": "Frequency", "value": ColorMode.Frequency},
            {"label": "Distance", "value": ColorMode.Distance},
        ],
    },
]


export default function ThreeChartsSettings({settings, setSettings}: {
    settings: ThreeChartsSettingsType;
    setSettings: (s: ThreeChartsSettingsType) => void
}): ReactElement {

    const updateSettingsProperty = (option: string, new_value: ColorMode | ProjectionMode | WindowMode): void => {
        const old_settings: ThreeChartsSettingsType = {...settings};
        // @ts-expect-error Dynamic write, I know for sure that option exists, so OK
        old_settings[option] = new_value;
        setSettings(old_settings);
    };

    return <Menu as="div" className="flex flex-col justify-end items-end">
        <Menu.Button
            className="shadow-lg rounded-full bg-white px-2 py-2 w-10 h-10 flex justify-center items-center">
            <WrenchIcon className="w-7 h-7 text-gray-700"/>
        </Menu.Button>
        <Transition
            as={Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform scale-50"
            enterTo="transform scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform scale-100"
            leaveTo="transform scale-50"
        >
            <Menu.Items className="bg-white rounded-xl p-3 mt-2 flex flex-col gap-y-3 shadow-lg">
                {radioSelections.map(category => <div>
                    <label className="text-base font-semibold text-gray-900">{category.label}</label>
                    <fieldset>
                        {category.options.map(option =>
                            <div className="flex items-center">
                                <input
                                    id={`${category.key}_${option.value}`}
                                    name={category.key}
                                    checked={settings[category.key as keyof ThreeChartsSettingsType] === option.value}
                                    type="radio"
                                    className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-offset-0 focus:ring-0"
                                    onClick={() => updateSettingsProperty(category.key, option.value)}
                                />
                                <label htmlFor={`${category.key}_${option.value}`}
                                       className="ml-3 block text-sm font-medium leading-6 text-gray-900">{option.label}</label>
                            </div>,
                        )}
                    </fieldset>
                </div>)}
            </Menu.Items>
        </Transition>
    </Menu>
}