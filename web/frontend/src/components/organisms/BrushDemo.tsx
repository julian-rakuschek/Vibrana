import {ReactElement, useEffect, useMemo, useRef} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import betterPointer from "lib/betterPointer";
import polygonClipping, {MultiPolygon, Pair, Polygon, Ring} from 'polygon-clipping';
import earcut from 'earcut';
import {distToNormalSegment, distToSegment} from "lib/util";
import {distancePairToLine, distancePairToOrthogonalLine, euclidean, polygonIntersects} from "lib/geometryUtil";
import RBush from 'rbush';

type Earcut = {
    vertices: number[],
    hole_indices: number[]
}

class MyRBush extends RBush {
    toBBox([x, y]) {
        return {minX: x, minY: y, maxX: x, maxY: y};
    }

    compareMinX(a, b) {
        return a.x - b.x;
    }

    compareMinY(a, b) {
        return a.y - b.y;
    }
}

const getCirlcePoints = (coords: [number, number], radius: number, n: number): Polygon => {
    const points: Pair[] = []
    for (let i = 0; i < n; i++) {
        const x = Math.cos(i / n * Math.PI * 2) * radius + coords[0];
        const y = Math.sin(i / n * Math.PI * 2) * radius + coords[1];
        points.push([x, y])
    }
    points.push([points[0][0], points[0][1]])
    return [points];
}


const polyToEarcut = (poly: Polygon): Earcut => {
    const flat: number[] = poly.flat(Infinity) as number[];
    const lenghts = poly.map(ring => ring.length);
    const indices = lenghts.map(((sum: number) => (value: number) => sum += value)(0));
    indices.pop()
    return {
        vertices: flat,
        hole_indices: indices
    }
}

const mousePolygon = (x: number, y: number, button: number, radius: number): number[][][] => {
    const points = getCirlcePoints([x, y], radius, 20);
    const triang = polyToTriangles(points);
    return triang.map(t => t.map(p => [...p, button]))
}

// const transformTriangulation = (triangulation: number[], poly: Polygon): Triangle[] => {
// }

const example_triang = (): number[][][] => {
    const flatToTriangles = arr => arr.reduce((result, value, index, array) => index % 3 === 0 ? [...result, [...array.slice(index, index + 3), array[index]]] : result, []);
    const points = getCirlcePoints([0.5, 0.5], 0.1, 10);
    const t = polyToEarcut(points)

    const tria = earcut(t.vertices, t.hole_indices)
    const tria2 = flatToTriangles(tria)
    const finito = tria2.map(t => t.map(t2 => points[0][t2]))
    return finito
}

const example_triang2 = (): number[][][] => {
    const flatToTriangles = arr => arr.reduce((result, value, index, array) => index % 3 === 0 ? [...result, [...array.slice(index, index + 3), array[index]]] : result, []);
    const points: Polygon = [[[0.1, 0.1], [0.1, 0.9], [0.9, 0.9], [0.9, 0.1]], [[0.3, 0.3], [0.3, 0.6], [0.6, 0.6], [0.6, 0.3]]];
    const t = polyToEarcut(points)
    const tria = earcut(t.vertices, t.hole_indices)
    const tria2 = flatToTriangles(tria)
    const finito = tria2.map(t => t.map(t2 => points.flat(1)[t2]))
    return finito
}

const example_cut = (): Ring[] => {
    const points: Polygon = [[[0.1, 0.1], [0.1, 0.9], [0.9, 0.9], [0.9, 0.1]], [[0.3, 0.3], [0.3, 0.6], [0.6, 0.6], [0.6, 0.3]]];
    const polys = ninja_cut(points)
    return polys
}

const polyToTriangles = (poly: Polygon): number[][][] => {
    const flatToTriangles = (arr: number[]) => {
        const polyFlat = poly.flat(1)
        const result = [];
        for (let i = 0; i < arr.length; i += 3) {
            result.push([
                polyFlat[arr[i]],
                polyFlat[arr[i + 1]],
                polyFlat[arr[i + 2]],
                polyFlat[arr[i]]
            ]);
        }
        return result;
    };


    const t = polyToEarcut(poly)
    const tria = earcut(t.vertices, t.hole_indices)
    return flatToTriangles(tria)
}

const ninja_cut = (poly: Polygon): Ring[] => {
    const res: Ring[] = []
    const with_holes: Polygon[] = [poly.filter(ring => ring.length > 3)]
    let i = 0

    while (with_holes.length > 0) {
        i++
        const poly_to_investigate = with_holes.pop()!
        if (poly_to_investigate.length == 1) {
            res.push(poly_to_investigate[0])
            continue
        }
        const outer_ring = poly_to_investigate[0]
        const hole = poly_to_investigate[1]
        if (hole.length < 4) {
            res.push(poly_to_investigate[0])
            continue
        }
        const a = hole[0]
        const b = hole[Math.ceil(hole.length / 2)]
        // console.log("Ring", hole)
        // console.log(a, b)
        const distances = outer_ring.map((ring_point, index) => [Math.abs(distancePairToLine(a, b, ring_point)), index])
        const normal_distances = outer_ring.map((ring_point) => distancePairToOrthogonalLine(a, b, ring_point))
        // console.log("Dist", distances)
        // console.log("Normal", normal_distances)
        // console.log("Dist filtered", distances.filter(r => normal_distances[r[1]] >= 0))
        // console.log("Dist filtered", distances.filter(r => normal_distances[r[1]] < 0))
        const outer_a = distances.filter(r => normal_distances[r[1]] >= 0).reduce((min, current) => current[0] < min[0] ? current : min)
        const outer_b = distances.filter(r => normal_distances[r[1]] < 0).reduce((min, current) => current[0] < min[0] ? current : min)
        const intersects = polygonIntersects(outer_ring[outer_a[1]], outer_ring[outer_b[1]], hole);
        if (!intersects) {
            with_holes.push([poly_to_investigate[0], ...poly_to_investigate.slice(2)])
            continue
        }
        // console.log(outer_a[1], outer_b[1])
        const boundary = outer_a[1] > outer_b[1] ? [outer_b[1], outer_a[1]] : [outer_a[1], outer_b[1]]
        let poly_a: Polygon = [[]]
        let poly_b: Polygon = [[]]
        for (let i = 0; i < outer_ring.length; i++) {
            if (i == boundary[0] || i == boundary[1]) {
                poly_a[0].push(outer_ring[i])
                poly_b[0].push(outer_ring[i])
            } else if (boundary[0] < i && i < boundary[1]) poly_a[0].push(outer_ring[i])
            else if (i < boundary[0] || boundary[1] < i) poly_b[0].push(outer_ring[i])
        }
        poly_a[0].push([poly_a[0][0][0], poly_a[0][0][1]])
        poly_b[0].push([poly_a[0][0][0], poly_a[0][0][1]])

        polygonClipping.difference(poly_to_investigate, poly_a).forEach(p => {
            p.length > 1 ? with_holes.push(p) : res.push(p[0])
        })
        polygonClipping.difference(poly_to_investigate, poly_b).forEach(p => {
            p.length > 1 ? with_holes.push(p) : res.push(p[0])
        })

        // poly_a = polygonClipping.difference(poly_to_investigate, poly_a)[0]
        // poly_b = polygonClipping.difference(poly_to_investigate, poly_b)[0]
        // poly_a.length > 1 ? with_holes.push(poly_a) : res.push(poly_a[0])
        // poly_b.length > 1 ? with_holes.push(poly_b) : res.push(poly_b[0])
        // console.log(poly_a)
        // console.log(poly_b)
        if (i > 100) {
            console.log(with_holes)
            console.log(res)
            console.log("Emergency break")
            break
        }
    }
    // console.log("Res before", res)
    for (let i = 0; i < res.length; i++) {
        res[i].push(res[i][0])
    }
    // console.log("Res after", res)
    return res
}

export default function BrushDemo(): ReactElement {
    const xScale = d3.scaleLinear()
    const yScale = d3.scaleLinear()
    const traceRef = useRef<number[][]>([])
    const polyRef = useRef<MultiPolygon>([]);
    const trianRef = useRef<number[][][]>([]);
    const last_point_ref = useRef<Pair | null>(null);
    const radius_ref = useRef<number>(0.035)
    const mouse_state = useRef<[number, number, number] | null>(null)
    const selected_indices = useRef<Set<number>>(new Set())

    const fillColors = ["navy", "lightgreen", "red"]
    const random_scatter = useMemo(() => [...Array(1000).keys()].map(i => [Math.random(), Math.random(), i]), [])
    const rtree = new MyRBush()
    rtree.load(random_scatter)
    const res = rtree.search({
        minX: 0.2,
        minY: 0.2,
        maxX: 0.7,
        maxY: 0.7
    });
    console.log(res)


    useEffect(() => {
        // trianRef.current = example_triang2();
        // trianRef.current = example_cut()
        render()
    }, []);

    function findPoints(x: number, y: number, radius: number) {
        const init_res = rtree.search({
            minX: x - radius,
            minY: y - radius,
            maxX: x + radius,
            maxY: y + radius
        })
        return init_res.filter(p => euclidean({x: p[0], y: p[1]}, {x, y}) < radius)
    }

    function handleBrush(x: number, y: number, button: number) {
        const points: MultiPolygon = [getCirlcePoints([x, y], radius_ref.current, 20)]
        if (polyRef.current === null) polyRef.current = points;
        else polyRef.current = button === 1 ? polygonClipping.union(polyRef.current, points) : polygonClipping.difference(polyRef.current, points);
        const scatterPoints = new Set(findPoints(x, y, radius_ref.current).map(p => p[2]));
        selected_indices.current = button === 1 ?
            new Set([...selected_indices.current, ...scatterPoints]) :
            new Set([...selected_indices.current].filter(x => !scatterPoints.has(x)));
        if (last_point_ref.current !== null) {
            const distance = Math.sqrt(Math.pow(x - last_point_ref.current[0], 2) + Math.pow(y - last_point_ref.current[1], 2))
            const n_fill_points = Math.floor(distance / (radius_ref.current / 2));
            const step_vector = [
                (x - last_point_ref.current[0]) / (n_fill_points + 1),
                (y - last_point_ref.current[1]) / (n_fill_points + 1)
            ];
            const current = [...last_point_ref.current]
            for (let i = 0; i < n_fill_points; i++) {
                current[0] += step_vector[0]
                current[1] += step_vector[1]
                const points_fill: MultiPolygon = [getCirlcePoints(current as Pair, radius_ref.current, 20)]
                polyRef.current = button === 1 ? polygonClipping.union(polyRef.current, points_fill) : polygonClipping.difference(polyRef.current, points_fill)
                const scatterPoints = new Set(findPoints(...current, radius_ref.current).map(p => p[2]));
        selected_indices.current = button === 1 ?
            new Set([...selected_indices.current, ...scatterPoints]) :
            new Set([...selected_indices.current].filter(x => !scatterPoints.has(x)));
            }
        }
        trianRef.current = polyRef.current.map(polyToTriangles).flat(1);
        // trianRef.current = polyRef.current.map(ninja_cut).flat(1);
        last_point_ref.current = [x, y]
    }

    function handleMouseEvent(coord: { x: number; y: number, buttons: number }) {
        if (!coord) {
            last_point_ref.current = null;
            return;
        }
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        mouse_state.current = [x, y, coord.buttons];

        if (coord.buttons === 0) {
            render()
            last_point_ref.current = null;
            return;
        }
        handleBrush(x, y, coord.buttons)
        render();
    }


    const trace = fc.seriesCanvasPoint().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        // selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
        context.fillStyle = selected_indices.current.has(index) ? "red" : "gray"
        context.strokeStyle = "transparent";
    });

    const trianglesD3 = fc.seriesCanvasLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((context, datum, index) => {
        // selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
        context.globalAlpha = 0.2;
        context.fillStyle = datum[0].length === 3 ? fillColors[datum[0][2]] : "gray"
        context.strokeStyle = "transparent";
    });

    const triangulationD3 = fc.seriesCanvasRepeat()
        .xScale(xScale)
        .yScale(yScale)
        .orient("horizontal")
        .series(trianglesD3);

    const triangulationMouseD3 = fc.seriesCanvasRepeat()
        .xScale(xScale)
        .yScale(yScale)
        .orient("horizontal")
        .series(trianglesD3);

    const pointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        handleMouseEvent(coord);
    })

    const pointerClick = betterPointer().on("click", ([coord]: { x: number; y: number, buttons: number }[]) => {
        handleBrush(coord.x, coord.y, 1)
    })

    const chart = fc
        .chartCartesian(xScale, yScale)
        .canvasPlotArea(fc.seriesCanvasMulti().series([trace, triangulationD3, triangulationMouseD3]).mapping((data, index, series) => {
            switch (series[index]) {
                case trace:
                    return data.trace;
                case triangulationD3:
                    return data.triangles;
                case triangulationMouseD3:
                    return data.mouse;
            }
        }))
        .decorate(sel =>
            sel
                .select("d3fc-canvas.plot-area")
                .call(pointer)
        );

    const reset = () => {
        traceRef.current = [];
        polyRef.current = [];
        trianRef.current = [];
        selected_indices.current = new Set()
        render();
    }

    const render = () => {
        d3.select(`#demo`).datum({
            trace: random_scatter,
            polygonOutline: [],
            triangles: trianRef.current,
            mouse: mouse_state.current !== null ? mousePolygon(...mouse_state.current, radius_ref.current) : []
        }).call(chart);
    };


    return <div className="p-10">
        <button type="button" onClick={() => reset()}
                className="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center  me-2 mb-2">
            Reset
        </button>
        <div id={"demo"} style={{width: 900, height: 900}} className="border-gray-700 border-2">
        </div>
    </div>
}