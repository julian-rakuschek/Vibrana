<script lang="ts">
    import {points} from "./landingPagePointCloud"
    import {onMount} from "svelte";

    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null
    const width = 800;
    const height = 800;
    let angle = 0;
    const max_scale = width * 10;
    const scales = new Array(points.length).fill(0);
    const scales_mask = new Array(points.length).fill(0);
    let max_animations = 500
    let active_animations = 20;
    for (let i = 0; i < active_animations; i++) {
        scales_mask[i] = 1;
        scales[i] = max_scale * (active_animations - i + 1) / active_animations;
    }

    function draw() {
        const findFirstZeroAfterOne = (arr: number[]): number => {
            let seenOne = false;
            return arr.findIndex(num => {
                if (seenOne && num === 0) return true;
                if (num === 1) seenOne = true;
                return false;
            });
        }

        if (!ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        angle += 0.003;

        for (let i = 0; i < points.length; i++) {
            const p = points[i];

            const x = p[0] * scales[i] * Math.cos(angle) - p[1] * scales[i] * Math.sin(angle);
            const y = p[0] * scales[i] * Math.sin(angle) + p[1] * scales[i] * Math.cos(angle);

            if (scales_mask[i] === 1) {
                scales[i] = Math.min(max_scale, scales[i] + 100)
                if (scales[i] === max_scale) {
                    scales_mask[i] = 0;
                    scales_mask[findFirstZeroAfterOne(scales_mask)] = 1;
                    if (active_animations < max_animations) {
                        scales_mask[findFirstZeroAfterOne(scales_mask)] = 1;
                        active_animations++;
                    }
                }
            }

            ctx.beginPath();
            ctx.arc(cx + x, cy + y, 1.5, 0, 2 * Math.PI);
            ctx.fillStyle = "#000";
            ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(cx, cy, 5, 0, 2 * Math.PI);
        ctx.fillStyle = "#FFF";
        ctx.strokeStyle = "rgba(1, 1, 1, 0)";
        ctx.fill();

        requestAnimationFrame(draw);
    }

    onMount(() => {
        ctx = canvas.getContext('2d')
        draw();
    })

</script>

<div class="w-full h-full grid place-items-center relative bg-[#faf9f5]">
    <div>
        <canvas height={height} width={width} bind:this={canvas}></canvas>
    </div>
    <div class="absolute grow flex flex-col items-center justify-center">
        <p class="text-[#141413] text-lg averia italic">Neo</p>
        <p class="text-[#141413] text-6xl averia">Vibrana</p>
        <div class="flex flex-col mt-4 gap-5">
            <a class="rounded-md text-center bg-[#141413] px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-[#141413] font-[Poppins]"
               href="/datasets">Explore Datasets</a>
        </div>
    </div>
</div>



