<script lang="ts">
    import * as d3 from "d3";
    import * as fc from "d3fc";
    import {type ProjectedPoint, type ThreeChartsSettingsType, type Point, WindowMode, type Label, type Annotation, type LabelBase} from "@lib/types";
    import {getContext, onMount} from "svelte";
    import {addAlphaToRGB, webglColor} from "@lib/helper/colorHelper";
    import betterPointer from "@lib/helper/betterPointer";
    import {filterRangeIndexed, filterRangePercent, chartSettings, hoverRange, hoverPoint, selectedProjectedPoints} from "@lib/stores";
    import {colorsTimeSeries} from "@lib/chartLogic/chartColors";
    import {selectedToColoredIntervals} from "@lib/helper/util";
    import {ApiRoutes} from "@lib/api/ApiRoutes";
    import {useQueryClient} from "@tanstack/svelte-query";
    import WindowSizePopup from "@components/WindowSizePopup.svelte";
    import {sessionAddLabel, sessionDeleteLabelPyPos} from "@lib/helper/sessionStorageHelper";

    export let machineId: string;
    export let sampleId: string;
    export let timeSeries: number[];
    export let projected: ProjectedPoint[];
    export let labels: Annotation[];
    export let events: number[];

    const client = useQueryClient()

    const timeseriesIndexed: Point[] = timeSeries.map((d, index) => ({x: index, y: d}))

    let brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, $chartSettings.windowSize)
    let addAnnotation = true;
    let windowSizeSelectionOpen = false;

    const min_value = Math.min(...timeSeries)
    const max_value = Math.max(...timeSeries)
    const xScale = d3.scaleLinear().domain([0, timeSeries.length]).range([0, 1]);
    const yScale = d3.scaleLinear().domain([min_value, max_value]).range([0, 1]);

    const {ro} = getContext("ro") as { ro: boolean }

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
    }).on("click", async ([coord]: { x: number; y: number }[]) => {
        if (!coord) return;
        const x = xScale.invert(coord.x);
        const selected = [
            Math.floor(Math.max(0, x - $chartSettings.windowSize / 2)),
            Math.floor(Math.min(timeSeries.length - 1, x + $chartSettings.windowSize / 2))
        ]
        if (addAnnotation) {
            const labelToAdd: LabelBase = {from: selected[0], to: selected[1], sampleId: sampleId, machine: machineId}
            if (ro) sessionAddLabel(labelToAdd)
            else await ApiRoutes.addLabel.fetch({data: labelToAdd})
        }
        else {
            if (ro) sessionDeleteLabelPyPos(machineId, sampleId, Math.floor(x))
            else await ApiRoutes.deleteLabelByPos.fetch({params: {pos: Math.floor(x), machineId: machineId, sampleId: sampleId}})
        }
        await client.invalidateQueries({queryKey: [`/db/labels/${machineId}/${sampleId}`]});
        await client.invalidateQueries({queryKey: [`/analysis/${machineId}/${sampleId}/similarities`]});
        render();
    });

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

    const savedAnnotations = fc
        .annotationSvgBand()
        .orient('vertical')
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
            se.selectAll('.band').attr('fill', 'rgba(0, 120, 0, 0.4)');
        });

    const eventMarker = fc
        .annotationSvgLine()
        .orient('vertical')
        .label('')
        .xScale(xScale)
        .yScale(yScale)
        .decorate(se => {
            se.selectAll('line')
                .style('stroke', 'rgba(255, 0, 0, 0.4)')  // Red color
                .style('stroke-width', '3px');          // Heavier stroke
        });

    const brushedSelectionAnnotations = fc
        .annotationSvgBand()
        .orient("vertical")
        .xScale(xScale)
        .yScale(yScale)
        .decorate((se, data) => {
            se.selectAll('.band').attr('fill', (d, i) => {
                const value = d.color || data[i].color;
                return addAlphaToRGB(d3.interpolateTurbo(value), 0.5)
            });
        });


    const navigatorChart = fc
        .chartCartesian(xScale, yScale)
        .webglPlotArea(fc.seriesWebglMulti().series([timeseriesLine]).mapping(d => d.data))
        .svgPlotArea(
            fc.seriesSvgMulti()
                .series([selectorHoverBand, brushedSelectionAnnotations, eventMarker, savedAnnotations])
                .mapping((data, index, series) => {
                    switch (series[index]) {
                        case selectorHoverBand:
                            return data.hover;
                        case brushedSelectionAnnotations:
                            return data.brushedIntervals;
                        case eventMarker:
                            return data.events;
                        case savedAnnotations:
                            return data.savedLabels;
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
            events: events,
            savedLabels: labels,
            brushed: $filterRangePercent,
            brushedIntervals: brushed
        }).call(navigatorChart)
    };

    filterRangeIndexed.subscribe((range) => {
        xScale.domain(range ? range : [0, timeSeries.length]);
        render()
    })

    hoverRange.subscribe(() => render())
    hoverPoint.subscribe(() => render())
    chartSettings.subscribe(() => {
        brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, $chartSettings.windowSize);
        render()
    })
    selectedProjectedPoints.subscribe(() => {
        brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, $chartSettings.windowSize);
        render()
    })
    colorsTimeSeries.subscribe(() => {
        brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, $chartSettings.windowSize);
        render()
    })
    $: {
        brushed = selectedToColoredIntervals($selectedProjectedPoints, $colorsTimeSeries, $chartSettings.windowSize);
        render();
    }

    $: labels, render();

    onMount(() => {
        render()
    })
</script>
<p class="text-center"><span class="font-semibold">Annotator</span>: <span class="text-black/70">Save intervals of the signal for later anomaly detection.</span> <button on:click={() => windowSizeSelectionOpen = true} class="cursor-default text-indigo-500 border-b-2 border-indigo-500 border-dotted hover:text-indigo-700 hover:border-indigo-700">Adjust Interval Size</button></p>
<div class="flex flex-row w-full justify-center gap-4">
    <button class={`flex flex-row justify-center items-center shadow-xl rounded-lg px-3 py-2 transition ${addAnnotation ? "bg-indigo-500 text-white" : "bg-white text-black"}`} on:click={() => addAnnotation = true}>
        <span class="leading-none">Add Annotation</span>
    </button>
    <button class={`flex flex-row justify-center items-center shadow-xl rounded-lg px-3 py-2 transition ${!addAnnotation ? "bg-indigo-500 text-white" : "bg-white text-black"}`} on:click={() => addAnnotation = false}>
        <span class="leading-none">Remove Annotation</span>
    </button>
</div>
<div id="annotator" style="height: 170px; width: 100%"></div>
<WindowSizePopup bind:isOpen={windowSizeSelectionOpen} timeSeries={timeSeries} />