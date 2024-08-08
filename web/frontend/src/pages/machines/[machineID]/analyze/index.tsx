import {ReactElement} from "react";
import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {PlusIcon} from "@heroicons/react/24/solid";
import {useParams} from "react-router-dom";
import SamplesList from "components/molecules/SamplesList";

export default function MachinePage(): ReactElement {
    const {machineID} = useParams();


    return <DefaultPageWithBoundaries showHeader >
        <div className="grow grid grid-cols-12">
            <div className="h-full col-span-8 border-r-2 border-dashed border-gray-700/50">
                <div className="w-full flex flex-row flex-nowrap justify-between px-5">
                    <span className="text-xl font-semibold">Samples</span>
                    <div className="bg-[#1c2934] rounded-lg px-3 py-2 text-white flex flex-row flex-nowrap items-center gap-2 cursor-default transition hover:bg-[#2d4253]"><PlusIcon className="w-5 h-5" /> Collect Sample</div>
                </div>
                {machineID && <SamplesList machine={machineID} />}
            </div>
            <div className="h-full col-span-4">
                <div className="w-full flex flex-row flex-nowrap justify-between px-5">
                    <span className="text-xl font-semibold">Live</span>
                </div>
            </div>
        </div>
    </DefaultPageWithBoundaries>
}