<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import {type ProjectedPoint, type ThreeChartsSettingsType, type Point, WindowMode, type Label} from "@lib/types";
    import {onMount} from "svelte";
    import {webglColor} from "@lib/helper/colorHelper";
    import betterPointer from "@lib/helper/betterPointer";
    import {filterRangeIndexed, filterRangePercent, chartSettings, hoverRange, hoverPoint} from "@lib/stores";
    import {colorsTimeSeries} from "@lib/chartLogic/chartColors";
    export let timeSeries: number[];
    export let projected: ProjectedPoint[];
    export let labels: Label[];
    export let events: number[];

    const timeseriesIndexed: Point[] = timeSeries.map((d, index) => ({
        x: index,
        y: d
    }))

    const min_value = Math.min(...timeSeries)
    const max_value = Math.max(...timeSeries)
    const xScale = d3.scaleLinear().domain([0, timeSeries.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const selectorPointer = betterPointer().on("point", ([coord]: { x: number; y: number }[]) => {
        if (!coord) return;
        const x = xScale.invert(coord.x);
        if ($chartSettings.window === WindowMode.Sliding) {
            hoverRange.set([
                Math.floor(Math.max(0, x - $chartSettings.windowSize / 2)),
                Math.floor(Math.min(timeSeries.length - 1, x + $chartSettings.windowSize / 2))
            ])
        } else {
            hoverRange.set([
                Math.floor(Math.max(0, Math.floor(x / $chartSettings.windowSize) * $chartSettings.windowSize)),
                Math.floor(Math.min(timeSeries.length - 1, Math.ceil(x / $chartSettings.windowSize) * $chartSettings.windowSize))
            ])
        }

        hoverPoint.set(projected.find(p => p.timeSeriesIndex === Math.floor(x)))

        render();
    })

    const timeseriesLine = fc
        .seriesWebglLine()
        .equals((previousData, currentData) => previousData === currentData)
        .crossValue((d: Point) => d.x)
        .mainValue((d: Point) => d.y)
        .decorate((program) => fc
            .webglStrokeColor()
            .value((d: Point) => {
                const col = $colorsTimeSeries[d.x].color
                return webglColor(col, 1)
            })
            .data(timeseriesIndexed)(program));

    const selectorHoverBand = fc
        .annotationSvgBand()
        .orient("vertical")
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 204, 0, 0.1)');
        });


    const navigatorChart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(
            fc.seriesSvgMulti()
                .series([selectorHoverBand])
                .mapping((data, index, series) => {
                    switch (series[index]) {
                        case selectorHoverBand:
                            return data.hover;
                    }
                })
        ).decorate(sel => sel.enter().select("d3fc-svg.plot-area").call(selectorPointer));

    const render = () => {
        d3.select(`#annotator`).datum({
            data: timeseriesIndexed,
            hover: [{
                from: $hoverRange ? $hoverRange[0] : 0,
                to: $hoverRange ? $hoverRange[1] : 0
            }],
        }).call(navigatorChart)
    };

    filterRangeIndexed.subscribe((range) => {
        xScale.domain(range ? range : [0, timeSeries.length]);
        render()
    })

    hoverRange.subscribe(() => render())
    hoverPoint.subscribe(() => render())
    chartSettings.subscribe(() => render())

    onMount(() => {
        render()
    })
</script>

<div id="annotator" style="height: 200px; width: 100%"></div>
