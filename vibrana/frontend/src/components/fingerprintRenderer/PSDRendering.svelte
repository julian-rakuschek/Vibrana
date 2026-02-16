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
        size?: number;
        showAxis?: boolean;
        color?: string;
    }

    let {
        frequencies = [],
        power = [],
        size = 200,
        showAxis = false,
        color = "black"
    }: Props = $props();

    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    let chart: Chart | null = null;

    function createChart(ctx: CanvasRenderingContext2D, power: number[], frequencies: number[]) {
        const dataPoints = frequencies.slice(0, frequencies.length / 3).map((f, i) => ({
            x: f,
            y: power[i] ?? 0
        }));


        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                datasets: [
                    {
                        label: "PSD",
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
                            display: true,
                            text: 'Frequency (Hz)',
                            padding: {top: 0}
                        }
                    },
                    y: {
                        display: false
                    }
                }
            }
        });
    }

    function render(power: number[], frequencies: number[]) {
        if (!context) return;

        const dataPoints = frequencies.slice(0, frequencies.length / 3).map((f, i) => ({
            x: f,
            y: power[i] ?? 0
        }));

        if (chart === null) {
            createChart(context, power, frequencies);
        } else {
            chart.data.datasets[0].data = dataPoints;
            chart.update();
        }
    }

    onMount(() => {
        context = canvas.getContext('2d');
        render(power, frequencies);
    })

    $effect(() => {
        render(power, frequencies);
    });

</script>

<div class="p-3" style={"height: {size}px; width: {size}px"}>
    <canvas height={size - 20} width={size - 20} bind:this={canvas}></canvas>
</div>
