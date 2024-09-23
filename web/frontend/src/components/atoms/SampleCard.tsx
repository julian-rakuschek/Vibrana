import {CheckCircleIcon as CheckCircleIconOutline} from "@heroicons/react/24/outline";
import {CheckCircleIcon as CheckCircleIconSolid} from "@heroicons/react/24/solid";
import AnomalyRatio from "components/atoms/AnomalyRatio";


export default function SampleCard({machine, sampleId, handleClick, selectModeActive, selected}: {machine: string; sampleId: string; handleClick: (s: string) => void; selectModeActive: boolean; selected: boolean}): JSX.Element {
    return <div
        onClick={() => handleClick(sampleId)}
        className={`overflow-hidden group border-2 border-solid border-transparent ${selectModeActive ? "hover:border-green-600" : ""} relative flex flex-col justify-center items-center w-[400px] h-[150px] shadow-lg rounded-lg px-2 transition hover:shadow-xl`}
    >
        {selectModeActive && selected && <div className="absolute top-1 left-1 hidden group-hover:block px-2 py-1">
            <CheckCircleIconOutline className="w-5 h-5 text-green-600"/>
        </div>}
        {selected &&
            <div className="absolute top-1 left-1 flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
                <CheckCircleIconSolid className="w-4 h-4 text-white"/> Anomaly-Free
            </div>}
        <img src={`/api/db/${machine}/samples/${sampleId}/thumbnail`} alt="thumbnail"/>
        <div className="flex flex-row justify-between items-center w-full mb-3">
            <span>{sampleId}</span>
            <AnomalyRatio machineId={machine} sampleId={sampleId}/>
        </div>
    </div>
}