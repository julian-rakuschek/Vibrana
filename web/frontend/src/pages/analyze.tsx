import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {useDummyValues, useDummyProjected} from "lib/hooks";
import * as fc from "d3fc"
import * as d3 from "d3"
import {useEffect, useMemo, useRef, useImperativeHandle, forwardRef, useState} from "react";
import NavigatorChart from "components/molecules/NavigatorChart";
import SelectionChart from "components/molecules/SelectionChart";
import TimeSeriesPathView from "components/molecules/TimeSeriesPathView";

export default function AnalyzePage(): JSX.Element {
    const values = useDummyValues();
    const projected = useDummyProjected();
    const selectorRef = useRef<{
        setRange: (range: number[]) => void
    }>(null);
    const scatterRef = useRef<{
        getSelectedPoint: () => number | undefined,
        setSelectedPoint: (value: number) => void
        setRange: (value: number[]) => void
    }>(null);
    const [currentSelectedPoint, setCurrentSelectedPoint] = useState<number | undefined>(100);
    const [brushedRange, setBrushedRange] = useState<number[] | null>(null);

    useEffect(() => {
        if (selectorRef && selectorRef.current && brushedRange) selectorRef.current.setRange(brushedRange)
    }, [brushedRange]);

    return (
        <DefaultPageWithBoundaries menuDarkMode>
            {values.length > 0 && <NavigatorChart onBrush={(new_range: number[]) => setBrushedRange(new_range)} data={values} chartId={"nav1"} height={200}/>}
            {values.length > 0 && <SelectionChart ref={selectorRef} data={values} chartId={"sel1"} height={200}/>}
            {projected.length > 0 &&
                <TimeSeriesPathView from_idx={brushedRange ? Math.floor(brushedRange[0] * projected.length) : 0} to_idx={brushedRange ? Math.floor(brushedRange[1] * projected.length) : values.length} ref={scatterRef} onSelectedPointChange={(value) => setCurrentSelectedPoint(value)}
                               data={projected} chartId={"scatter1"} height={600} width={"100%"}/>}
        </DefaultPageWithBoundaries>
    );
}