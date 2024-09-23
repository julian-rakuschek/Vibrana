import {ReactElement, useState} from "react";
import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {useParams} from "react-router-dom";
import SamplesList from "components/molecules/SamplesList";
import SampleSettings from "components/molecules/SamplesSettings";
import {SamplesSettingsType, SortMode} from "../../../../types";

export default function MachinePage(): ReactElement {
    const {machineID} = useParams();
    const [selectModeActive, setSelectModeActive] = useState(false)
    const [settings, setSettings] = useState<SamplesSettingsType>({sort: SortMode.Score, split: false})

    return <DefaultPageWithBoundaries showHeader >
        <div className="grow grid grid-cols-12">
            <div className="h-full col-span-full px-10 ">
                <div className="w-full flex flex-row flex-nowrap justify-between relative z-50">
                    <span className="text-xl font-semibold">Samples</span>
                    <div onClick={() => setSelectModeActive(!selectModeActive)}
                         className={`${selectModeActive ? "bg-green-600 text-white" : "bg-white text-green-600"}  border-green-600 border-2 border-solid rounded-lg px-3 py-1 mr-20 flex flex-row flex-nowrap items-center gap-2 cursor-default transition`}
                    >
                        {!selectModeActive ? "Select Anomaly-Free Samples" : "Exit Selection Mode"}
                    </div>
                    <div className="absolute top-0 right-0">
                        {machineID && <SampleSettings settings={settings} setSettings={setSettings} machine={machineID} />}
                    </div>
                </div>
                {machineID && <SamplesList machine={machineID} selectModeActive={selectModeActive} settings={settings} />}
            </div>
            <div className="h-full col-span-4 hidden">
                <div className="w-full flex flex-row flex-nowrap justify-between px-5">
                    <span className="text-xl font-semibold">Live</span>
                </div>
            </div>
        </div>
    </DefaultPageWithBoundaries>
}