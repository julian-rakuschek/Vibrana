import {ReactElement} from "react";
import {useAnomalyScore} from "lib/hooks";

export default function AnomalyRatio({ machineId, sampleId }: { machineId: string; sampleId: string}): ReactElement {
    let anomalyRatio = useAnomalyScore(machineId, sampleId)
    if(anomalyRatio) anomalyRatio = Math.round(anomalyRatio * 10000) / 100

    return <span>
        {anomalyRatio ?? ""}
    </span>
}