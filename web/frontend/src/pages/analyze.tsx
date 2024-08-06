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
    const [hoverRange, setHoverRange] = useState<number | undefined>(100);
    const [brushedRange, setBrushedRange] = useState<number[] | null>(null);
    const [windowSize, setWindowSize] = useState(100);

    useEffect(() => {
        if (selectorRef && selectorRef.current && brushedRange) selectorRef.current.setRange(brushedRange)
        if (scatterRef && scatterRef.current) {
            scatterRef.current.setRange(
                [brushedRange ? Math.floor(brushedRange[0] * projected.length) : 0, brushedRange ? Math.floor(brushedRange[1] * projected.length) : values.length]
            )
        }
    }, [brushedRange]);

    useEffect(() => {

    }, [hoverRange]);

    return (
        <DefaultPageWithBoundaries menuDarkMode>
            {values.length > 0 && projected.length > 0 &&
                <div className="flex flex-col p-5 gap-5">
                    <NavigatorChart
                        onBrush={(new_range: number[]) => setBrushedRange(new_range)}
                        data={values} chartId={"nav1"} height={150}
                    />
                    <SelectionChart windowSize={windowSize} setWindowSize={setWindowSize} ref={selectorRef} data={values} chartId={"sel1"} height={200} />
                    <TimeSeriesPathView
                        ref={scatterRef} onHoverChange={(value) => setHoverRange(value)}
                        data={projected} chartId={"scatter1"} height={500} width={"100%"} windowSize={windowSize}
                    />
                </div>}
        </DefaultPageWithBoundaries>
    );
}