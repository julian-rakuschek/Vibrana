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
        data?: number[];
        size?: number;
        showYAxis?: boolean;
        color?: string;
    }

    let {
        data = [],
        size = 200,
        showYAxis = false,
        color = "black"
    }: Props = $props();

    let canvas: HTMLCanvasElement = $state();
    let context: CanvasRenderingContext2D | null;
    let chart: Chart | null = null;

    function createChart(ctx: CanvasRenderingContext2D, values: number[]) {
        const default_labels = Array.from({length: values.length}, (x, i) => i);

        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: default_labels,
                datasets: [
                    {
                        label: "PSD",
                        data: values,
                        borderColor: color,
                        backgroundColor: color,
                        order: 10
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {intersect: false, mode: 'index'},
                animation: false,
                plugins: {
                    legend: {
                        display: false,
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: showYAxis
                    }
                }
            }
        });
    }

    function render(values: number[]) {
        if (!context) return;
        if (chart === null) {
            createChart(context, values);
        } else {
            const default_labels = Array.from({length: values.length}, (x, i) => i);
            chart.data.labels = default_labels
            chart.data.datasets[0].data = values;
            chart.update()
        }
    }

    onMount(() => {
        context = canvas.getContext('2d');
        render(data);
    })

    $effect(() => {
        render(data);
    });

</script>

<div class="p-3" style={"height: {size}px; width: {size}px"}>
    <canvas height={size - 20} width={size - 20} bind:this={canvas}></canvas>
</div>
