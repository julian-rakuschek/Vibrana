import type {Point} from "../types";
import type {Pair, Ring} from "polygon-clipping";
import {line} from "d3";

export function euclidean(p1: Point, p2: Point) {
    return Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2)
}

function dotProduct(p1: Point, p2: Point): number {
    return p1.x * p2.x + p1.y * p2.y;
}

function subtractPoints(p1: Point, p2: Point): Point {
    return {x: p1.x - p2.x, y: p1.y - p2.y};
}

function addPoints(p1: Point, p2: Point): Point {
    return {x: p1.x + p2.x, y: p1.y + p2.y};
}

function scalarMultiply(scalar: number, p: Point): Point {
    return {x: scalar * p.x, y: scalar * p.y};
}

function normalize(p: Point): Point {
    const d = Math.sqrt(dotProduct(p, p))
    return {x: p.x / d, y: p.y / d}
}

function projectPointOntoLine(line_a: Point, line_b: Point, query: Point): Point {
    const AB = subtractPoints(line_b, line_a);
    const AC = subtractPoints(query, line_a);
    const dotACAB = dotProduct(AC, AB);
    const dotABAB = dotProduct(AB, AB);
    const scalar = dotACAB / dotABAB;
    return addPoints(line_a, scalarMultiply(scalar, AB));
}

export function distanceToLine(line_a: Point, line_b: Point, query: Point) {
    const projected = projectPointOntoLine(line_a, line_b, query)
    const dist = euclidean(query, projected)
    const AB = subtractPoints(line_b, line_a);
    const projectedVector =  normalize(subtractPoints(query, projected));
    const normal_vector = normalize({x: -AB.y, y: AB.x})
    const sign = dotProduct(normal_vector, projectedVector) > 0 ? 1 : -1
    return dist * sign
}


export function distanceToOrthogonalLine(line_a: Point, line_b: Point, query: Point) {
    const axis = [(line_a.x + line_b.x) / 2, (line_a.y + line_b.y) / 2]
    const q = [line_a.x - axis[0], line_a.y - axis[1]]
    const q_prime = [-q[1], q[0]]
    const rotated = [q_prime[0] + axis[0], q_prime[1] + axis[1]]
    return distanceToLine(
        {x: rotated[0], y: rotated[1]},
        {x: axis[0], y: axis[1]},
        {x: query.x, y: query.y},
    )
}

export function distancePairToLine(line_a: Pair, line_b: Pair, query: Pair) {
    return distanceToLine(
        {x: line_a[0], y: line_a[1]},
        {x: line_b[0], y: line_b[1]},
        {x: query[0], y: query[1]},
    )
}

export function distancePairToOrthogonalLine(line_a: Pair, line_b: Pair, query: Pair) {
    return distanceToOrthogonalLine(
        {x: line_a[0], y: line_a[1]},
        {x: line_b[0], y: line_b[1]},
        {x: query[0], y: query[1]},
    )
}

function lineOrientation(a: Pair, b: Pair, c: Pair) {
    const mat = [
        [a[0] - c[0], a[1] - c[1]],
        [b[0] - c[0], b[1] - c[1]],
    ]
    const det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0];
    if (det < 0) return -1
    else if (det > 0) return 1
    else return 0
}

export function polygonIntersects(line_a: Pair, line_b: Pair, polygon: Ring) {
    for (let i = 1; i < polygon.length; i++) {
        const side_q = lineOrientation(line_a, line_b, polygon[i - 1]);
        const side_p = lineOrientation(line_a, line_b, polygon[i]);
        if (side_p !== side_q) return true;
    }
    return false;
}