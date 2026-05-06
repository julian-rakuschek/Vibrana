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
        power?: number[];
        width?: number;
        height?: number;
        showAxis?: boolean;
        showYAxis?: boolean;
        color?: string;
    }

    let {
        frequencies = [],
        power = [],
        width = 200,
        height = 200,
        showAxis = false,
        showYAxis = false,
        color = "black"
    }: Props = $props();

    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    let chart: Chart | null = null;

    function getVisibleFrequencies(frequencies: number[]) {
        return frequencies.slice(0, frequencies.length);
    }

    function getDataPoints(power: number[], frequencies: number[]) {
        return getVisibleFrequencies(frequencies).map((f, i) => ({
            x: f,
            y: power[i] ?? 0
        }));
    }

    function getAxisMax(power: number[]) {
        const max = Math.max(...power.filter(Number.isFinite), 0);
        return max > 0 ? max * 1.05 : 1;
    }

    function formatPowerTick(value: string | number) {
        const numericValue = Number(value);
        if (!Number.isFinite(numericValue)) return `${value}`;
        if (numericValue === 0) return "0";
        if (Math.abs(numericValue) < 0.01 || Math.abs(numericValue) >= 1000) {
            return numericValue.toExponential(1);
        }
        return numericValue.toLocaleString(undefined, {maximumSignificantDigits: 3});
    }

    function createChart(ctx: CanvasRenderingContext2D, power: number[], frequencies: number[]) {
        const dataPoints = getDataPoints(power, frequencies);

        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                datasets: [
                    {
                        label: "Magnitude",
                        data: dataPoints,
                        borderColor: color,
                        backgroundColor: color,
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
                        display: showYAxis,
                        min: 0,
                        max: getAxisMax(power),
                        border: {
                            display: showYAxis
                        },
                        grid: {
                            display: showYAxis,
                            color: "rgba(17, 24, 39, 0.12)"
                        },
                        ticks: {
                            maxTicksLimit: 5,
                            callback: formatPowerTick
                        },
                        title: {
                            display: showYAxis,
                            text: "Magnitude",
                            padding: {bottom: 0}
                        }
                    }
                }
            }
        });
    }

    function render(power: number[], frequencies: number[], color: string, showAxis: boolean, showYAxis: boolean) {
        if (!context) return;

        const dataPoints = getDataPoints(power, frequencies);

        if (chart === null) {
            createChart(context, power, frequencies);
        } else {
            chart.data.datasets[0].data = dataPoints;
            chart.data.datasets[0].borderColor = color;
            chart.data.datasets[0].backgroundColor = color;
            chart.options.scales!.x!.display = showAxis;
            chart.options.scales!.x!.title!.display = showAxis;
            chart.options.scales!.y!.display = showYAxis;
            chart.options.scales!.y!.max = getAxisMax(power);
            chart.options.scales!.y!.border!.display = showYAxis;
            chart.options.scales!.y!.grid!.display = showYAxis;
            chart.options.scales!.y!.title!.display = showYAxis;
            chart.update();
        }
    }

    onMount(() => {
        context = canvas.getContext('2d');
        render(power, frequencies, color, showAxis, showYAxis);
    })

    $effect(() => {
        render(power, frequencies, color, showAxis, showYAxis);
    });

</script>

<div class="p-3" style={"height: {height}px; width: {width}px"}>
    <canvas height={height - 20} width={width - 20} bind:this={canvas}></canvas>
</div>
