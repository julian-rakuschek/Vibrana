import {ReactElement} from "react";
import {useAnomalyScores, useNormals, useSamples} from "lib/hooks";
import {useNavigate} from "react-router-dom";
import {CheckCircleIcon as CheckCircleIconOutline} from "@heroicons/react/24/outline";
import {CheckCircleIcon as CheckCircleIconSolid} from "@heroicons/react/24/solid";
import {ApiRoutes} from "lib/api/ApiRoutes";
import {useQueryClient} from "@tanstack/react-query";
import AnomalyRatio from "components/atoms/AnomalyRatio";
import {SamplesSettingsType, SortMode} from "../../types";
import SampleCard from "components/atoms/SampleCard";

export default function SamplesList({machine, selectModeActive, settings}: { machine: string; selectModeActive: boolean; settings: SamplesSettingsType }): ReactElement {
    const samples = useSamples(machine);
    const anomaly_ratios = useAnomalyScores(machine);
    const navigate = useNavigate();
    const normals = useNormals(machine);
    const queryClient = useQueryClient();

    let sample_sorted = samples.sort();
    if (settings.sort === SortMode.Score && anomaly_ratios && samples) {
        sample_sorted = anomaly_ratios.map(s => s[0])
    }

    const handleClick = async (sampleId: string) => {
        if (selectModeActive) {
            if (normals.indexOf(sampleId) === -1) {
                await ApiRoutes.addNormal.fetch({params: {machineId: machine, sampleId: sampleId}})
            }
            else {
                await ApiRoutes.removeNormal.fetch({params: {machineId: machine, sampleId: sampleId}})
            }
            await queryClient.invalidateQueries();
        }
        else navigate(`/machines/${machine}/analyze/${sampleId}`)
    }

    return <div className="flex flex-row flex-wrap gap-6 py-4 justify-center">
        {!settings.split && sample_sorted.map(s => <SampleCard machine={machine} sampleId={s} handleClick={handleClick} selectModeActive={selectModeActive} selected={normals.indexOf(s) !== -1} />)}
        {settings.split && <div className="flex flex-row gap-20">
            <div className="flex flex-col gap-4">
                {sample_sorted
                    .filter(s => s.startsWith("normal"))
                    .map(s => <SampleCard machine={machine} sampleId={s} handleClick={handleClick} selectModeActive={selectModeActive} selected={normals.indexOf(s) !== -1}/>)
                }
            </div>
            <div className="flex flex-col gap-4">
                {sample_sorted
                    .filter(s => s.startsWith("abnormal"))
                    .map(s => <SampleCard machine={machine} sampleId={s} handleClick={handleClick} selectModeActive={selectModeActive} selected={normals.indexOf(s) !== -1}/>)
                }
            </div>
        </div>}
    </div>
}