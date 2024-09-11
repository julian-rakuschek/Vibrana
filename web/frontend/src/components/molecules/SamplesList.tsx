import {ReactElement} from "react";
import {useNormals, useSamples} from "lib/hooks";
import {Link, useNavigate} from "react-router-dom";
import {CheckCircleIcon as CheckCircleIconOutline} from "@heroicons/react/24/outline";
import {CheckCircleIcon as CheckCircleIconSolid} from "@heroicons/react/24/solid";
import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryClient} from "@tanstack/react-query";

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
                {selectModeActive && normals.indexOf(s) === -1 && <div className="absolute top-1 left-1 hidden group-hover:block">
                    <CheckCircleIconOutline className="w-5 h-5 text-green-600"/>
                </div>}
                {normals.indexOf(s) !== -1 && <div className="absolute top-1 left-1">
                    <CheckCircleIconSolid className="w-5 h-5 text-green-600"/>
                </div>}
                <img src={`/api/db/${machine}/samples/${s}/thumbnail`} alt="thumbnail"/>
                <span className="mb-4">{s}</span>

            </div>)}
    </div>
}