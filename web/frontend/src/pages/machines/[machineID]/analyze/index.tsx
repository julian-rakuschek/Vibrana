import {ReactElement, useState} from "react";
import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {PlusIcon} from "@heroicons/react/24/solid";
import {useParams} from "react-router-dom";
import SamplesList from "components/molecules/SamplesList";

export default function MachinePage(): ReactElement {
    const {machineID} = useParams();
    const [selectModeActive, setSelectModeActive] = useState(false)

    return <DefaultPageWithBoundaries showHeader >
        <div className="grow grid grid-cols-12">
            <div className="h-full col-span-8 border-r-2 border-dashed border-gray-700/50 px-10 ">
                <div className="w-full flex flex-row flex-nowrap justify-between">
                    <span className="text-xl font-semibold">Samples</span>
                    <div onClick={() => setSelectModeActive(!selectModeActive)}
                         className={`${selectModeActive ? "bg-green-600 text-white" : "bg-white text-green-600"}  border-green-600 border-2 border-solid rounded-lg px-3 py-1 flex flex-row flex-nowrap items-center gap-2 cursor-default transition`}
                    >
                        {!selectModeActive ? "Select Anomaly-Free Samples" : "Exit Selection Mode"}
                    </div>
                </div>
                {machineID && <SamplesList machine={machineID} selectModeActive={selectModeActive} />}
            </div>
            <div className="h-full col-span-4">
                <div className="w-full flex flex-row flex-nowrap justify-between px-5">
                    <span className="text-xl font-semibold">Live</span>
                </div>
            </div>
        </div>
    </DefaultPageWithBoundaries>
}