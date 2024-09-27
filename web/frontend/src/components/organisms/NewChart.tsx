import {ReactElement, useMemo, useRef, useState} from "react";
import {
    useClusteredProjection,
    useLabels, useNormalBand,
    useSampleEvents,
    useSampleProjected,
    useSampleValues,
    useSimilarities
} from "lib/hooks";
import {compute_colors} from "components/organisms/ThreeChartsWrapper";
import {ProjectionMode, ThreeChartsSettingsType} from "../../types";
import NavigatorChart, {
    filterRangeIndexedAtom,
    filterRangePercentAtom
} from "components/organisms/newCharts/NavigatorChart";
import {largestTriangleThreeBuckets, minMaxDecimation} from "lib/util";
import {useAtomValue} from "jotai";
import AnnotatorChart from "components/organisms/newCharts/AnnotatorChart";
import {lab} from "d3";
import ScatterChart from "components/organisms/newCharts/ScatterChart";

const getReducedTS = (timeseries: number[], colors: string[]): { ts: number[], c: string[] } => {
    const res = minMaxDecimation(timeseries, 1000)
    const delta = timeseries.length / res.length;
    const colors_reduced = [];
    for (let i = 0; i < timeseries.length; i = i + delta) {
        colors_reduced.push(colors[Math.floor(i)]);
    }
    return {ts: res, c: colors_reduced}
}


export default function NewChart({machineId, sampleId, settings}: {
    machineId: string;
    sampleId: string;
    settings: ThreeChartsSettingsType
}): ReactElement {
    const navigatorRef = useRef();

    const filterRangePercent = useAtomValue(filterRangePercentAtom)
    const timeseries = useSampleValues(machineId, sampleId);
    const projected = useSampleProjected(machineId, sampleId);
    const clustered = useClusteredProjection(machineId, sampleId, settings.window_size);
    const labels = useLabels(machineId, sampleId);
    const events = useSampleEvents(machineId, sampleId)
    const similarities = useSimilarities(machineId, sampleId);
    const normal_tube = useNormalBand(machineId);
    const [chartKey, setChartKey] = useState(0);
    const offset = timeseries.length - projected.length
    const colors = compute_colors(settings, projected, similarities, normal_tube, offset);
    const min_value = useMemo(() => Math.min(...timeseries), [timeseries])
    const max_value = useMemo(() => Math.max(...timeseries), [timeseries])

    const nav_reduced = useMemo(() => getReducedTS(timeseries, colors.colors_ts), [timeseries, colors])
    const ann_reduced = useMemo(() => getReducedTS(
        filterRangePercent ? timeseries.slice(filterRangePercent[0] * timeseries.length, filterRangePercent[1] * timeseries.length) : timeseries,
        filterRangePercent ? colors.colors_ts.slice(filterRangePercent[0] * timeseries.length, filterRangePercent[1] * timeseries.length) : colors.colors_ts,
    ), [filterRangePercent, timeseries, colors])

    const handleReset = () => {
        if (navigatorRef.current) {
            navigatorRef.current.reset();
        }
    };

    return <>
        <button onClick={handleReset}>
            Reset
        </button>
        {false && timeseries.length > 0 && projected.length > 0 && clustered.length > 0 &&
            <NavigatorChart
                ref={navigatorRef}
                chartId={"new"}
                timeseries={nav_reduced.ts}
                labels={labels}
                settings={settings}
                events={events}
                colors_ts={nav_reduced.c}
            />
        }
        {false && <AnnotatorChart timeseries={ann_reduced.ts} labels={labels} settings={settings} chartId={"ann"} events={events}
                        colors_ts={ann_reduced.c} min_value={min_value} max_value={max_value}/>}
        <ScatterChart projected={projected} labels={labels} settings={settings} chartId={"pro"} events={events} colors_projected={colors.colors_projected} tsIndexOffset={offset} />
    </>
}