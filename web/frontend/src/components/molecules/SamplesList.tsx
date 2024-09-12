import {ReactElement} from "react";
import {useAnomalyScore, useNormals, useSamples} from "lib/hooks";
import {Link, useNavigate} from "react-router-dom";
import {CheckCircleIcon as CheckCircleIconOutline, CheckIcon} from "@heroicons/react/24/outline";
import {CheckCircleIcon as CheckCircleIconSolid} from "@heroicons/react/24/solid";
import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryClient} from "@tanstack/react-query";
import AnomalyRatio from "components/atoms/AnomalyRatio";

export default function SamplesList({machine, selectModeActive}: { machine: string; selectModeActive: boolean }): ReactElement {
    const samples = useSamples(machine);
    const navigate = useNavigate();
    const normals = useNormals(machine);
    const queryClient = useQueryClient();

    const handleClick = async (sampleId: string) => {
        if (selectModeActive) {
            if (normals.indexOf(sampleId) === -1) {
                const res = await ApiRoutes.addNormal.fetch({params: {machineId: machine, sampleId: sampleId}})
            }
            else {
                const res = await ApiRoutes.removeNormal.fetch({params: {machineId: machine, sampleId: sampleId}})
            }
            await queryClient.invalidateQueries();
        }
        else navigate(`/machines/${machine}/analyze/${sampleId}`)
    }

    return <div className="flex flex-row flex-wrap gap-6 p-4 justify-center">
        {samples.map(s =>
            <div
                onClick={() => handleClick(s)}
                className={`overflow-hidden group border-2 border-solid border-transparent ${selectModeActive ? "hover:border-green-600" : ""} relative flex flex-col justify-center items-center w-[400px] h-[150px] shadow-lg rounded-lg px-2 transition hover:shadow-xl`}
            >
                {selectModeActive && normals.indexOf(s) === -1 && <div className="absolute top-1 left-1 hidden group-hover:block px-2 py-1">
                    <CheckCircleIconOutline className="w-5 h-5 text-green-600"/>
                </div>}
                {normals.indexOf(s) !== -1 && <div className="absolute top-1 left-1 flex flex-row flex-nowrap text-xs gap-1 justify-center items-center bg-green-600 rounded-full px-2 py-1 text-white font-semibold">
                    <CheckCircleIconSolid className="w-4 h-4 text-white"/> Anomaly-Free
                </div>}
                <img src={`/api/db/${machine}/samples/${s}/thumbnail`} alt="thumbnail"/>
                <div className="flex flex-row justify-between items-center w-full mb-3">
                    <span>{s}</span>
                    <AnomalyRatio machineId={machine} sampleId={s}/>
                </div>
            </div>)}
    </div>
}