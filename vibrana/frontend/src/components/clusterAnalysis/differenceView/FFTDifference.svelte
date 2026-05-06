<script lang="ts">
    import {onMount} from "svelte";
    import {
        BarController,
        BarElement,
        CategoryScale,
        Chart,
        Legend,
        LinearScale,
        LineController,
        LineElement,
        PointElement,
        ScatterController,
        Tooltip
    } from "chart.js";

    Chart.register(ScatterController, LineController, LinearScale, CategoryScale, PointElement, LineElement, Tooltip, Legend, BarElement, BarController);

    interface Props {
        frequencies?: number[];
        delta?: number[];
        size?: number;
        showAxis?: boolean;
    }

    let {
        frequencies = [],
        delta = [],
        size = 200,
        showAxis = false,
    }: Props = $props();

    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    let chart: Chart | null = null;

    function blendWithWhite(color: [number, number, number], weight: number) {
        const clampedWeight = Math.max(0, Math.min(1, weight));
        const channels = color.map((channel) => Math.round(255 - (255 - channel) * clampedWeight));
        return `rgb(${channels.join(", ")})`;
    }

    function getDeltaColor(value: number, maxAbsDelta: number) {
        if (maxAbsDelta === 0) return "rgb(255, 255, 255)";
        const intensity = Math.abs(value) / maxAbsDelta;
        return blendWithWhite(value >= 0 ? [30, 64, 175] : [185, 28, 28], intensity);
    }

    function getVisibleFrequencies(frequencies: number[]) {
        return frequencies.slice(0, frequencies.length / 3);
    }

    function getDataPoints(delta: number[], frequencies: number[]) {
        return getVisibleFrequencies(frequencies).map((f, i) => ({
            x: f,
            y: delta[i] ?? 0
        }));
    }

    function getMaxAbsDelta(delta: number[]) {
        return Math.max(...delta.map((value) => Math.abs(value)), 0);
    }

    function getAxisMax(delta: number[]) {
        return getMaxAbsDelta(delta) || 1;
    }

    function createChart(ctx: CanvasRenderingContext2D, delta: number[], frequencies: number[]) {
        const dataPoints = getDataPoints(delta, frequencies);
        const maxAbsDelta = getMaxAbsDelta(delta);
        const axisMax = getAxisMax(delta);
        const colors = dataPoints.map((point) => getDeltaColor(point.y, maxAbsDelta));

        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                datasets: [
                    {
                        label: "PSD Delta",
                        data: dataPoints,
                        borderColor: colors,
                        backgroundColor: colors,
                        base: 0,
                        parsing: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {intersect: false, mode: 'index'},
                animation: false,
                plugins: {
                    legend: {display: false}
                },
                scales: {
                    x: {
                        display: showAxis,
                        type: 'linear',
                        offset: false,
                        bounds: 'data',
                        grid: {
                            display: false
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 10,
                            maxRotation: 0
                        },
                        title: {
                            display: showAxis,
                            text: 'Frequency (Hz)',
                            padding: {top: 0}
                        }
                    },
                    y: {
                        display: true,
                        min: -axisMax,
                        max: axisMax,
                        border: {
                            display: false
                        },
                        grid: {
                            color: (context) => context.tick.value === 0 ? "#111827" : "transparent",
                            lineWidth: (context) => context.tick.value === 0 ? 1 : 0
                        },
                        ticks: {
                            display: showAxis,
                            maxTicksLimit: 5
                        }
                    }
                }
            }
        });
    }

    function render(delta: number[], frequencies: number[]) {
        if (!context) return;

        const dataPoints = getDataPoints(delta, frequencies);
        const maxAbsDelta = getMaxAbsDelta(delta);
        const axisMax = getAxisMax(delta);
        const colors = dataPoints.map((point) => getDeltaColor(point.y, maxAbsDelta));

        if (chart === null) {
            createChart(context, delta, frequencies);
        } else {
            chart.data.datasets[0].data = dataPoints;
            chart.data.datasets[0].borderColor = colors;
            chart.data.datasets[0].backgroundColor = colors;
            chart.options.scales!.y!.min = -axisMax;
            chart.options.scales!.y!.max = axisMax;
            chart.update();
        }
    }

    onMount(() => {
        context = canvas.getContext('2d');
        render(delta, frequencies);
    })

    $effect(() => {
        render(delta, frequencies);
    });

</script>

<div class="p-3" style={"height: {size}px; width: {size}px"}>
    <canvas height={size - 20} width={size - 20} bind:this={canvas}></canvas>
</div>
