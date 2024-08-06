import {forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";

const SelectionChart = forwardRef(({chartId, data, width, height, windowSize, setWindowSize, onHoverChange}: {
    chartId: string;
    data: number[];
    width?: number;
    height?: number;
    windowSize: number;
    setWindowSize: (w: number) => void;
    onHoverChange?: (range: number[] | undefined) => void;
}, ref) => {
    const id = chartId === undefined ? "line" : chartId;
    const hoverRange = useRef<number[]>([0, 0]);
    const brushedRange = useRef<number[] | undefined>(undefined);
    const [mode, setMode] = useState("annotation")
    const transformed = useMemo(() => data.map((d, index) => {
        return {x: index, y: d}
    }), [chartId])
    const min_value = useMemo(() => Math.min(...data), [chartId])
    const max_value = useMemo(() => Math.max(...data), [chartId])
    const xScale = d3.scaleLinear().domain([0, data.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    const pointer = fc.pointer().on("point", ([coord]) => {
        if (!coord) return;
        const x = xScale.invert(coord.x);
        hoverRange.current = [Math.max(0, x - windowSize / 2), Math.min(data.length - 1, x + windowSize / 2)]
        render();
    });

    const pointSeries = fc.seriesWebglLine()
        .crossValue(d => d.x)
        .mainValue(d => d.y)


    const brush = fc.brushX().on('brush', e => {
        if (e.selection) {
            brushedRange.current = e.selection;
            setWindowSize(Math.floor(Math.abs(e.selection[0] - e.selection[1]) * data.length))
            render();
        }
    });

    const verticalBand = fc
        .annotationSvgBand()
        .orient('vertical')
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 204, 0, 0.1)');
        });

    const hoverBand = fc.annotationSvgBand()
        .orient("vertical")
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 204, 0, 0.1)');
        });

    const chart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(
            fc
                .seriesWebglMulti()
                .series([pointSeries])
                .mapping(d => d.data)

        )
        .svgPlotArea(
            fc.seriesSvgMulti()
                .series([verticalBand, hoverBand, brush])
                .mapping((data, index, series) => {
                    switch (series[index]) {
                        case verticalBand:
                            return data.selected;
                        case hoverBand:
                            return data.hover;
                        case brush:
                            return data.brushedRange;
                    }
                })
        )
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")
                .call(pointer)
        );

    const render = () => {
        d3.select(`#${id}`).datum({
            data: transformed,
            selected: {from: 10000, to: 30000},
            brushedRange: brushedRange.current,
            hover: {from: hoverRange.current[0], to: hoverRange.current[1]}
        }).call(chart)
    };
    useEffect(() => {
        render()
    }, [data.length, chartId]);

    useEffect(() => {
        brushedRange.current = undefined
        render();
    }, [mode]);

    useImperativeHandle(ref, () => ({
        setRange: (range: number[]) => {
            xScale.domain([data.length * range[0], data.length * range[1]]);
            render();
        }
    }));

    return (
        <div className="rounded-xl shadow-lg text-center flex flex-col items-center">
            <div className="flex flex-row shadow-xl rounded-lg bg-white px-2 py-1 cursor-default">
                <div onClick={() => setMode("size")}
                     className={`${mode === "size" ? 'bg-indigo-700-accent text-white ' : 'bg-white text-gray-800/80'} px-3 rounded-lg `}>Select
                    window size ({windowSize})
                </div>
                <div onClick={() => setMode("annotation")}
                     className={`${mode === "annotation" ? 'bg-indigo-700-accent text-white' : 'bg-white text-gray-800/80'} px-3 rounded-lg `}>Draw
                    annotation
                </div>
                <div onClick={() => setMode("delete")}
                     className={`${mode === "delete" ? 'bg-indigo-700-accent text-white' : 'bg-white text-gray-800/80'} px-3 rounded-lg `}>Delete
                    annotation
                </div>
            </div>

            <div
                id={id}
                style={{
                    width: width != undefined ? width : "100%",
                    height: height != undefined ? height : "95vh"
                }}
            ></div>
        </div>
    );
});

export default SelectionChart;