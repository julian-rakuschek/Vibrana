import {Fragment, ReactElement} from "react";
import {Menu, Transition} from "@headlessui/react";
import {WrenchIcon} from "@heroicons/react/24/solid";
import {SamplesSettingsType, SortMode, ToastType} from "../../types";
import Toggle from "components/atoms/Toggle";
import {ApiRoutes} from "lib/api/ApiRoutes";
import {useSetAtom} from "jotai";
import {toastAtom} from "components/atoms/Toast";
import {useQueryClient} from "@tanstack/react-query";

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


export default function SampleSettings({settings, setSettings, machine}: {
    settings: SamplesSettingsType;
    setSettings: (s: SamplesSettingsType) => void;
    machine: string;
}): ReactElement {
    const setToast = useSetAtom(toastAtom);
    const queryClient = useQueryClient();

    const updateSettingsProperty = (option: string, new_value: SortMode): void => {
        const old_settings: SamplesSettingsType = {...settings};
        // @ts-expect-error Dynamic write, I know for sure that option exists, so OK
        old_settings[option] = new_value;
        setSettings(old_settings);
    };

    const reset = async (): void => {
        const res = await ApiRoutes.reset.fetch({params: {machine}});
        if (res.success) setToast({ type: ToastType.Success, message: "Labels resetted" })
        else setToast({ type: ToastType.Error, message: "Reset failed" });
        await queryClient.invalidateQueries();
    }

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
                {radioSelections.map(category => <div key={category.key}>
                    <label className="text-base font-semibold text-gray-900">{category.label}</label>
                    <fieldset>
                        {category.options.map(option =>
                            <div className="flex items-center" key={`${category.key}_${option.value}`}>
                                <input
                                    id={`${category.key}_${option.value}`}
                                    name={category.key}
                                    checked={settings[category.key as keyof SamplesSettingsType] === option.value}
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
                <div className="flex flex-col">
                    <label className="text-base font-semibold text-gray-900">Split by Ground Truth</label>
                    <Toggle enabled={settings.split} setEnabled={() => updateSettingsProperty("split", !settings.split)}/>
                </div>
                <button className="text-sm text-red-500 bg-red-300/50 rounded-lg transition hover:bg-red-500 hover:text-white" onClick={() => reset()}>Reset Labels</button>
            </Menu.Items>
        </Transition>
    </Menu>
}