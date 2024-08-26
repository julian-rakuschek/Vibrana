import {ReactElement, useEffect, useRef} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import {ProjectionMode} from "../../types";
import betterPointer from "lib/betterPointer";

export default function BrushDemo(): ReactElement {
    const xScale = d3.scaleLinear()
    const yScale = d3.scaleLinear()
    const traceRef = useRef<number[][]>([]);

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const pointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        if (!coord || coord.buttons === 0) return;
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        traceRef.current = [...traceRef.current, [x, y]]
        render();
    })

    const trace = fc.seriesSvgPoint().crossValue(d => d[0]).mainValue(d => d[1])

    const projectionChart = fc
        .chartCartesian(xScale, yScale)
    .svgPlotArea(fc.seriesSvgMulti().series([trace]).mapping((data, index, series) => {
            switch (series[index]) {
                case trace:
                    return data.trace;
            }
        }))
     .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")
            .call(pointer)
     );



    const render = () => {
        d3.select("#Demo").datum({trace: traceRef.current}).call(projectionChart)
    }

    useEffect(() => {
        render()
    }, []);

    return <div
        id={"Demo"}
        className="border-2 border-gray-500 border-solid m-10"
        style={{
            width: 600,
            height: 600,
        }}
    ></div>
}