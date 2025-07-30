<script lang="ts">
    import {onMount} from 'svelte';
    import * as d3 from 'd3';
    import type {D3DragEvent} from 'd3';
    import {ApiRoutes} from '@lib/api/ApiRoutes';
    import type {DistributionWeights, Fingerprint} from '@lib/types';
    import {ColorMode} from "@lib/types";
    import ColorLegend from '@components/atoms/ColorLegend.svelte';
    import {computeIndexAllocationArray} from "@lib/helper/fingerprintHelper";

    export let dataset: string;
    export let subset: string;
    export let fingerprints: Fingerprint[];

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D | null;
    export let width = 0;
    const height = 200;
    const radius = 3;
    const selectRadius = radius * 5;
    let numberPoints = 10;
    let aging: number[] = [];

    type Circle = { x: number; y: number; active: boolean; index: number }
    type DragEvenet = D3DragEvent<HTMLCanvasElement, unknown, Circle>;
    let circles: Circle[] = [];

    function render() {
        if (!context) return;
        context.clearRect(0, 0, width, height);
        const max = aging.toSorted((a, b) => a - b)[aging.length - 1];
        const min = -1;
        const colorScale = d3.scaleSequential(d3.interpolateViridis).domain([min, max === -1 ? 1 : max]);

        context.beginPath();
        circles.sort((a, b) => a.index - b.index);
        const path = new Path2D(lineGenerator(circles) ?? '');
        context.strokeStyle = '#9fa8da';
        context.lineWidth = 2;
        context.stroke(path);

        const gradient = context.createLinearGradient(0, 0, width, 0);
        aging.forEach((d, i) => {
            gradient.addColorStop(i / (aging.length - 1), colorScale(d));
        });
        context.fillStyle = gradient;
        context.fill(path);

        for (const {x, y, active} of circles) {
            context.beginPath();
            context.moveTo(x + radius, y);
            context.arc(x, y, radius, 0, 2 * Math.PI);
            context.fillStyle = '#9fa8da';
            context.fill();
            if (active) {
                context.lineWidth = 2;
                context.stroke();
            }
        }
    }

    const lineGenerator = d3.area<Circle>().curve(d3.curveBumpX).x(d => d.x).y0(height).y1(d => d.y);


    function drag(circles: Circle[]) {
        function dragsubject(event: DragEvenet) {
            let subject = null;
            let distance = selectRadius;
            for (const c of circles) {
                let d = Math.sqrt(Math.pow(event.x - c.x, 2) + Math.pow(event.y - c.y, 2));
                if (d < distance) {
                    distance = d;
                    subject = c;
                }
            }
            return subject;
        }

        function dragstarted(event: DragEvenet) {
            circles.splice(circles.indexOf(event.subject), 1);
            circles.push(event.subject);
            event.subject.active = true;
        }

        function dragged(event: DragEvenet) {
            event.subject.y = Math.max(radius, Math.min(height - radius, event.y));
        }


        async function dragended(event: DragEvenet) {
            event.subject.active = false;
            await handleUpdate();
        }

        return d3.drag()
            .subject(dragsubject)
            .on('start', (event) => {
                dragstarted(event);
                render();
            })
            .on('drag', (event) => {
                dragged(event);
                render();
            })
            .on('end', (event) => {
                dragended(event);
                render();
            });
    }

    function samplePath(pathString: string, numPoints: number): { x: number; y: number }[] {
        const svgPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        svgPath.setAttribute('d', pathString);

        const length = svgPath.getTotalLength();
        const points = [];

        for (let i = 0; i < numPoints; i++) {
            const pos = svgPath.getPointAtLength((i / (numPoints - 1)) * length);
            points.push({x: pos.x, y: height - pos.y});
        }

        return points;
    }

    async function handleUpdate() {
        const lineGenerator = d3.line<Circle>().curve(d3.curveBumpX).x(d => d.x).y(d => d.y);
        const sampledPoints = samplePath(lineGenerator(circles)!, width);
        const data: DistributionWeights = {
            controlPoints: circles,
            curve: sampledPoints
        };
        await ApiRoutes.storeParameters.fetch({data: {weights: data}, params: {dataset, subset}});
    }

    const reset = async () => {
        circles.forEach(c => c.y = height - 10);
        render();
        await handleUpdate();
    };

    onMount(async () => {
        const data = await ApiRoutes.getParameters.fetch({params: {dataset, subset}})
        context = canvas.getContext('2d');
        // circles = data.weights.controlPoints.length > 0 ? data.weights.controlPoints : d3.range(numberPoints).map(i => ({



        circles = d3.range(numberPoints).map(i => ({
            x: i / (numberPoints - 1) * (width - radius * 2) + radius,
            y: height - 10,
            active: false,
            index: i
        }));
        d3.select(canvas).call(drag(circles, context));
        aging = computeIndexAllocationArray(fingerprints, width, -1);
        render();
    });

    $: {
        aging = computeIndexAllocationArray(fingerprints, width, -1);
        render();
    }

</script>
<div class="w-full">
    <div class="h-[30px] bg-purple-900 text-white" style={`width: ${width}px`}>
    <p>{width}</p>
    </div>
    <canvas bind:this={canvas} width={width} height={height}></canvas>
    <button on:click={() => reset()} class="text-indigo-600 px-4 pt-1 hover:text-indigo-800">Reset Curve</button>
    <p class="italic text-wrap p-4"><b>Steering</b> Adjust the curve by dragging points up or down to change the
        probability that the algorithm will compute a fingerprint at that point.
        The color beneath the curve indicates the age of each fingerprint: darker shades represent older fingerprints,
        while brighter shades show more recent computation results.</p>
    <div class="w-1/2">
        <ColorLegend colorMode={ColorMode.Age}/>
    </div>
</div>
