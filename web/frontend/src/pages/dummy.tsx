import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {useDummyValues, useDummyProjected} from "lib/hooks";
import * as fc from "d3fc"
import * as d3 from "d3"
import {useEffect, useMemo, useRef, useImperativeHandle, forwardRef, useState} from "react";

const webglColor = (color: string) => {
    const {r, g, b, opacity} = d3.color(color).rgb();
    return [r / 255, g / 255, b / 255, opacity];
};



const SimpleScatter = forwardRef(({chartId, data, width, height, onSelectedPointChange}: {
    chartId: string;
    data: number[][];
    width?: number;
    height?: number;
    onSelectedPointChange?: (selectedPoint: number | undefined) => void;
}, ref) => {

    const id = chartId === undefined ? "scatter" : chartId;
    const padding = 0.1;
    const min_x_value = useMemo(() => Math.min(...data.map(d => d[0])), [chartId])
    const max_x_value = useMemo(() => Math.max(...data.map(d => d[0])), [chartId])
    const min_y_value = useMemo(() => Math.min(...data.map(d => d[1])), [chartId])
    const max_y_value = useMemo(() => Math.max(...data.map(d => d[1])), [chartId])
    const dataWithIndex = data.map((d, i) => ({index: i, coords: d}));
    const quadtree = d3.quadtree<{ index: number; coords: number[] }>()
        .x(d => d.coords[0])
        .y(d => d.coords[1])
        .addAll(dataWithIndex);

    const xScale = d3.scaleLinear()
        .domain([min_x_value - Math.abs(min_x_value - max_x_value) * padding, max_x_value + Math.abs(min_x_value - max_x_value) * padding])
        .range([0, 1]);
    const yScale = d3.scaleLinear()
        .domain([min_y_value - Math.abs(min_y_value - max_y_value) * padding, max_y_value + Math.abs(min_y_value - max_y_value) * padding])
        .range([0, 1])

    const xScaleOriginal = xScale.copy();
    const yScaleOriginal = yScale.copy();
    const selectedPoint = useRef<number | undefined>(100);

    useImperativeHandle(ref, () => ({
        getSelectedPoint: () => selectedPoint.current,
        setSelectedPoint: (value: number) => {
            selectedPoint.current = value;
            render();
        }
    }));

    const pointer = fc.pointer().on("point", ([coord]) => {
        if (!coord || !quadtree) return;
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        const radius = Math.abs(xScale.invert(coord.x) - xScale.invert(coord.x - 20));
        const closestDatum = quadtree.find(x, y, radius);
        selectedPoint.current = closestDatum?.index;
        if (onSelectedPointChange) onSelectedPointChange(selectedPoint.current);
        render();
    });


    const fillColor = fc
        .webglFillColor()
        .value(d => selectedPoint.current === undefined ? webglColor("lightgray") : webglColor(d.index > selectedPoint.current - 10 && d.index < selectedPoint.current + 10 ? "red" : "lightgray"))
        .data(dataWithIndex);

    const pointSeries = fc
        .seriesWebglPoint()
        .equals((a, b) => a === b)
        .size(20)
        .crossValue(d => d.coords[0])
        .mainValue(d => d.coords[1])
        .decorate(s => fillColor(s))

    const trace = fc.seriesSvgLine()
        .crossValue(d => d[0])
        .mainValue(d => d[1])

    const chart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(
            fc
                .seriesWebglMulti()
                .series([pointSeries])
                .mapping(d => d.data)
        )
        .svgPlotArea(
            fc
                .seriesSvgMulti()
                .series([trace])
                .mapping(d => d.trace)
        )
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")

                .on("measure.range", (event) => {
                    xScaleOriginal.range([0, event.detail.width]);
                    yScaleOriginal.range([event.detail.height, 0]);
                })
                .call(zoom)
                .call(pointer)
        );

    const render = () => {
        d3.select(`#${id}`).datum({
            data: dataWithIndex,
            trace: selectedPoint.current ? data.slice(selectedPoint.current - 10, selectedPoint.current + 10) : []
        }).call(chart)
    };

    const zoom = d3
        .zoom()
        .on("zoom", (event) => {
            xScale.domain(event.transform.rescaleX(xScaleOriginal).domain());
            yScale.domain(event.transform.rescaleY(yScaleOriginal).domain());
            render();
        });

    useEffect(() => {
        render()
    }, [data.length, chartId]);
    return (
        <div
            id={id}
            style={{
                width: width != undefined ? width : "400px",
                height: height != undefined ? height : "400px"
            }}
        ></div>
    );
});

export default function Home(): JSX.Element {
    const values = useDummyValues();
    const projected = useDummyProjected();
    const scatterRef = useRef<{
        getSelectedPoint: () => number | undefined,
        setSelectedPoint: (value: number) => void
    }>(null);
    const [currentSelectedPoint, setCurrentSelectedPoint] = useState<number | undefined>(100);

    return (
        <DefaultPageWithBoundaries menuDarkMode>
            {values.length > 0 && <SimpleChart data={values} chartId={"chart1"} height={200}/>}
            {projected.length > 0 &&
                <SimpleScatter ref={scatterRef} onHoverChange={(value) => setCurrentSelectedPoint(value)}
                               data={projected} chartId={"scatter1"} height={600} width={"100%"}/>}
        </DefaultPageWithBoundaries>
    );
}