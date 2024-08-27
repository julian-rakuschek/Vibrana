import {ReactElement, useEffect, useRef} from "react";
import * as d3 from "d3";
import * as fc from "d3fc";
import betterPointer from "lib/betterPointer";
import polygonClipping, {MultiPolygon, Pair, Polygon} from 'polygon-clipping';
import earcut from 'earcut';

type Earcut = {
    vertices: number[],
    hole_indices: number[]
}

type Triangle = [Pair, Pair, Pair]

const transformTo2D = arr => arr.reduce((result, value, index, array) => index % 2 === 0 ? [...result, array.slice(index, index + 2)] : result, []);

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
    const lenghts = poly.map(ring => ring.length * 2);
    const indices = lenghts.map(((sum: number) => (value: number) => sum += value)(0));
    indices.pop()
    return {
        vertices: flat,
        hole_indices: indices
    }
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

const polyToTriangles = (poly: Polygon): number[][][] => {
    const flatToTriangles = arr => arr.reduce((result, value, index, array) => index % 3 === 0 ? [...result, [...array.slice(index, index + 3), array[index]]] : result, []);

    const t = polyToEarcut(poly)
    const tria = earcut(t.vertices, t.hole_indices)
    const tria2 = flatToTriangles(tria)
    const finito = tria2.map(t => t.map(t2 => poly.flat(1)[t2]))
    return finito
}

export default function BrushDemo(): ReactElement {
    const xScale = d3.scaleLinear()
    const yScale = d3.scaleLinear()
    const traceRef = useRef<number[][]>([])
    const polyRef = useRef<MultiPolygon>([]);
    const trianRef = useRef<number[][][]>([]);

    const trace = fc.seriesSvgPoint().crossValue(d => d[0]).mainValue(d => d[1])

    const polygonOutline = fc.seriesSvgPoint()
        .crossValue(d => d[0])
        .mainValue(d => d[1])
        .size(d => 8)
        .decorate(sel => {
            sel.enter().attr('fill', d => "#1f77b4").attr('stroke', d => null);
        });

    const trianglesD3 = fc.seriesSvgLine().crossValue(d => d[0]).mainValue(d => d[1]).decorate((selection) => {
        selection.enter().attr('fill', 'lightblue').attr('stroke', 'navy').attr("opacity", 0.2);
    })

    const triangulationD3 = fc.seriesSvgRepeat()
        .xScale(xScale)
        .yScale(yScale)
        .orient("horizontal")
        .series(trianglesD3);

    const pointer = betterPointer().on("point", ([coord]: { x: number; y: number, buttons: number }[]) => {
        if (!coord || coord.buttons === 0) return;
        const x = xScale.invert(coord.x);
        const y = yScale.invert(coord.y);
        traceRef.current = [...traceRef.current, [x, y]];
        const points: MultiPolygon = [getCirlcePoints([x, y], 0.1, 20)]
        if (polyRef.current === null) polyRef.current = points;
        else polyRef.current = polygonClipping.union(polyRef.current, points)
        console.log(polyRef.current)
        trianRef.current = polyRef.current.map(polyToTriangles).flat(1);
        render();
    })

    const chart = fc
        .chartCartesian(xScale, yScale)
        .svgPlotArea(fc.seriesSvgMulti().series([trace, polygonOutline, triangulationD3]).mapping((data, index, series) => {
            switch (series[index]) {
                case trace:
                    return data.trace;
                case polygonOutline:
                    return data.polygonOutline;
                case triangulationD3:
                    return data.triangles;
            }
        }))
        .decorate(sel =>
            sel
                .enter()
                .select("d3fc-svg.plot-area")
                .call(pointer)
        );

    const reset = () => {
        traceRef.current = [];
        polyRef.current = [];
        trianRef.current = [];
        render();
    }

    const render = () => {
        const triangles = example_triang()
        d3.select(`#demo`).datum({
            trace: traceRef.current,
            polygonOutline: [],
            triangles: trianRef.current
        }).call(chart);
    };

    useEffect(() => {
        render()
    }, []);

    return <div className="p-10">
        <button type="button" onClick={() => reset()}
                className="text-gray-900 bg-gray-100 hover:bg-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center  me-2 mb-2">
            Reset
        </button>
        <div id={"demo"} style={{width: 600, height: 600}} className="border-gray-700 border-2">
        </div>
    </div>
}