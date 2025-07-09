<script lang="ts">
	import * as d3 from 'd3';
	import * as fc from 'd3fc';
	import { DemoRBush, DummyClusterRBush, mousePolygon } from '@lib/helper/brushHelper';
	import betterPointer from '@lib/helper/betterPointer';
	import { onMount } from 'svelte';
	import { DBSCAN_Scatter } from '@lib/algorithms/incrementalDBSCAN';
	import type {ClusterHistogram, ScatterPoint} from '@lib/types';
	import {rgbStringToHex} from "@lib/helper/colorHelper.js";

	const getRandomNumber = (min: number, max: number) => Math.random() * (max - min) + min;


	const xScale = d3.scaleLinear();
	const yScale = d3.scaleLinear();

	let radius = 0.035;
	let mouseState: [number, number, number] | null = null;

	let scatter_points: ScatterPoint[] = [];
	let dbscan = new DBSCAN_Scatter(0.05, 10, scatter_points);
	let cluster_histogram: ClusterHistogram = dbscan.get_cluster_distribution();

	let brush_active: boolean = false;

	function handleMouseEvent(coord: { x: number; y: number, buttons: number }, singleClick: boolean) {
		if (!coord) {
			return;
		}
		if (!brush_active && !singleClick) return;
		const x = xScale.invert(coord.x);
		const y = yScale.invert(coord.y);
		mouseState = [x, y, coord.buttons];

		if (coord.buttons === 0) {
			render();
			return;
		}
		const random_radius = getRandomNumber(0, radius);
		const random_angle = getRandomNumber(0, 2 * Math.PI);
		let new_point: ScatterPoint = {x: x, y: y, index: scatter_points.length};
		if (brush_active) {
			new_point = {
				x: x + Math.cos(random_angle) * random_radius,
				y: y + Math.sin(random_angle) * random_radius,
				index: scatter_points.length
			};
		}
		scatter_points = [...scatter_points, new_point];
		dbscan.insert(new_point);
		cluster_histogram = dbscan.get_cluster_distribution();
		render();
	}


	const scatterPlot = fc.seriesCanvasPoint().crossValue(d => d.x).mainValue(d => d.y).decorate((context, datum, index) => {
		context.fillStyle = dbscan.getColor(index);
		context.strokeStyle = 'transparent';
	});

	const trianglesD3 = fc.seriesCanvasLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
		context.globalAlpha = 0.2;
		context.fillStyle = 'gray';
		context.strokeStyle = 'transparent';
	});

	const triangulationMouseD3 = fc.seriesCanvasRepeat()
		.xScale(xScale)
		.yScale(yScale)
		.orient('horizontal')
		.series(trianglesD3);

	const pointer = betterPointer().on('point', ([coord]: { x: number; y: number, buttons: number }[]) => {
		handleMouseEvent(coord, false);
	}).on('click', ([coord]: { x: number; y: number, buttons: number }[]) => {
		handleMouseEvent(coord, true);
	});

	const chart = fc
		.chartCartesian(xScale, yScale)
		.canvasPlotArea(fc.seriesCanvasMulti().series([scatterPlot, triangulationMouseD3]).mapping((data, index, series) => {
			switch (series[index]) {
				case scatterPlot:
					return data.scatter;
				case triangulationMouseD3:
					return data.mouse;
			}
		}))
		.decorate(sel =>
			sel
				.select('d3fc-canvas.plot-area')
				.call(pointer)
		);

	const reset = () => {
		scatter_points = [];
		dbscan.reset();
		cluster_histogram = [];
		render();
	};

	const render = () => {
		d3.select(`#demo`).datum({
			scatter: scatter_points,
			polygonOutline: [],
			mouse: mouseState !== null && brush_active ? mousePolygon(...mouseState, radius) : []
		}).call(chart);
	};

	const cluster = () => {
		const res = dbscan.cluster();
		cluster_histogram = dbscan.get_cluster_distribution();
		console.log(res);
		render();
		// const distinct_clusters = Array.from(new Set(cluster_labels.filter(r => r !== -1)));
		// let distinct_cluster_colors: string[] = createColorsArray(distinct_clusters.length, { start: 0, end: 1, reverse: false, interpolateFunc: interpolateTurbo })
		// cluster_colors = cluster_labels.map(l => l === -1 ? "gray" : distinct_cluster_colors[distinct_clusters.indexOf(l)]);
	};

	onMount(() => {
		render();
	});

</script>
<div class="p-10">
<p class="text-3xl">Incremental DBSCAN Demo</p>
	<button on:click={() => reset()}
			class="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center me-2 mb-2">
		Reset
	</button>
	<button on:click={() => cluster()}
			class="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center me-2 mb-2">
		Cluster
	</button>
	<button on:click={() => brush_active = !brush_active}
			class={`${brush_active ? "text-white bg-indigo-600 hover:bg-indigo-700" : "text-gray-900 bg-gray-100 hover:bg-gray-200"}  font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center me-2 mb-2`}>
		Brush Active
	</button>
	<div class="flex flex-row">
		<div id={"demo"} class="border-gray-700 border-2" style="width: 800px; height: 800px"></div>
		<div class="px-6">
			<p>Cluster Details</p>
			<div class="grid grid-cols-6 place-items-start gap-2">
				{#each cluster_histogram as cluster}
					<p class="text-right place-self-end" style={`color: ${cluster.color}`}>{cluster.cluster_id}</p>
					<div class="h-[20px] col-span-4" style={`background-color: ${cluster.color}; width: ${cluster.relative_size * 100}%`}></div>
					<p style={`color: ${cluster.color}`}>{cluster.size} members</p>
				{/each}
			</div>
		</div>
	</div>
</div>