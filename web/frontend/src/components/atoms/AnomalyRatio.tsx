import {ReactElement} from "react";
import {useAnomalyScore} from "lib/hooks";
import {interpolateRdYlBu, color} from "d3";
import {colorIsDarkSimple} from "lib/util";

const min_percentage = 0
const max_percentage = 0.1

export default function AnomalyRatio({ machineId, sampleId }: { machineId: string; sampleId: string}): ReactElement {
    let anomalyRatio = useAnomalyScore(machineId, sampleId)
    if (anomalyRatio === undefined || isNaN(anomalyRatio)) return <></>

    anomalyRatio = Math.round(anomalyRatio * 10000) / 100
    const background_color = interpolateRdYlBu(1 - (anomalyRatio - min_percentage) / (max_percentage - min_percentage))
    const text_color = colorIsDarkSimple(color(background_color).hex()) ? '#FFFFFF' : '#000000';

    return <div style={{backgroundColor: background_color, color: text_color}} className="w-[50px] flex flex-row justify-center items-center text-center rounded-lg p-0 h-[20px] text-xs">
        <span>{anomalyRatio ?? ""}</span>
    </div>
}