import {ReactElement} from "react";
import {useLabels, useSampleProjected, useSampleValues} from "lib/hooks";
import ThreeCharts from "components/organisms/ThreeCharts";
import {ThreeChartsSettingsType} from "../../types";

export default function ThreeChartsWrapper({machineId, sampleId, settings}: {machineId: string; sampleId: string; settings: ThreeChartsSettingsType}): ReactElement {
    const timeseries = useSampleValues(machineId, sampleId);
    const projected = useSampleProjected(machineId, sampleId);
    const labels = useLabels(machineId, sampleId);

    return <>
        {timeseries.length > 0 && projected.length > 0 && <ThreeCharts sampleId={sampleId} machineId={machineId} timeseries={timeseries} labels={labels} projected={projected} settings={settings} />}
    </>
}