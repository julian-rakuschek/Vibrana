<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import type { D3DragEvent } from 'd3';

	let canvas: HTMLCanvasElement;
	let context: CanvasRenderingContext2D | null;
	const width = 500;
	const height = 500;
	const radius = 3;
	const selectRadius = radius * 2;
	const numberPoints = 40;


	type Circle = { x: number; y: number; active: boolean; index: number }
	type DragEvenet = D3DragEvent<HTMLCanvasElement, unknown, Circle>;
	let circles: Circle[] = [];

	function render() {
		if (!context) return;
		context.clearRect(0, 0, width, height);
		const colorScale = d3.scaleSequential(d3.interpolateViridis).domain([0, 1]);
		const stops = [0.4, 0.1, 0.3, 1, 0.1, 0];

		context.beginPath();
		circles.sort((a, b) => a.index - b.index);
		const path = new Path2D(lineGenerator(circles) ?? '');
		context.strokeStyle = '#303f9f';
		context.lineWidth = 2;
		context.stroke(path);

		const gradient = context.createLinearGradient(0, 0, width, 0);
		stops.forEach((d, i) => {
			gradient.addColorStop(i / (stops.length - 1), colorScale(d));
		});
		context.fillStyle = gradient;
		context.fill(path);

		for (const { x, y, active } of circles) {
			context.beginPath();
			context.moveTo(x + radius, y);
			context.arc(x, y, radius, 0, 2 * Math.PI);
			context.fillStyle = '#1a237e';
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
			// event.subject.x = Math.max(radius, Math.min(width - radius, event.x));
			event.subject.y = Math.max(radius, Math.min(height - radius, event.y));
		}

		function dragended(event: DragEvenet) {
			event.subject.active = false;
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

	onMount(() => {
		context = canvas.getContext('2d');
		circles = d3.range(numberPoints).map(i => ({
			x: i / numberPoints * width + radius,
			y: height / 2,
			active: false,
			index: i
		}));
		d3.select(canvas).call(drag(circles, context));
		render();
	});
</script>
<div>
	<canvas bind:this={canvas} width={width} height={height}></canvas>
</div>