import {ReactElement, useEffect, useState} from "react";
import {useClusteredProjection, useLabels, useSampleProjected, useSampleValues} from "lib/hooks";
import ThreeCharts from "components/organisms/ThreeCharts";
import {ProjectionMode, ThreeChartsSettingsType} from "../../types";

export default function ThreeChartsWrapper({machineId, sampleId, settings}: {
    machineId: string;
    sampleId: string;
    settings: ThreeChartsSettingsType
}): ReactElement {
    const timeseries = useSampleValues(machineId, sampleId);
    const projected = useSampleProjected(machineId, sampleId);
    const clustered = useClusteredProjection(machineId, sampleId, settings.window_size);
    const labels = useLabels(machineId, sampleId);
    const [chartKey, setChartKey] = useState(0);

    useEffect(() => {
        setChartKey(chartKey + 1);
    }, [settings]);

    return <>
        {timeseries.length > 0 && projected.length > 0 && clustered.length > 0 &&
            <ThreeCharts
                key={chartKey}
                sampleId={sampleId} machineId={machineId} timeseries={timeseries}
                labels={labels}
                projected={settings.projection === ProjectionMode.Paths ? projected : clustered}
                settings={settings}
            />
        }
    </>
}