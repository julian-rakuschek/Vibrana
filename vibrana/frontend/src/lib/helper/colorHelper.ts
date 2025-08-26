import * as d3 from "d3";
import Color from "colorjs.io";

export type ColorInterpolateParams = {
  start: number;
  end: number;
  reverse: boolean;
  interpolateFunc: (t: number) => string;
};

// Src: https://medium.com/code-nebula/automatically-generate-chart-colors-with-chart-js-d3s-color-scales-f62e282b2b41
export function createColorsArray(dataLength: number, colorInterpolateParams: ColorInterpolateParams): string[] {
  const colorRange = colorInterpolateParams.end - colorInterpolateParams.start;
  const intervalSize = colorRange / dataLength;
  const colorArray = [];

  for(let i = 0; i < dataLength; i++) {
    const colorPoint: number = colorInterpolateParams.reverse ?
      (colorInterpolateParams.end - (i * intervalSize)) :
      (colorInterpolateParams.start + (i * intervalSize));
    colorArray.push(colorInterpolateParams.interpolateFunc(colorPoint));
  }

  return colorArray;
}

export function getSingleColor(value: number, colorInterpolateParams: ColorInterpolateParams): string {
  const colorRange = colorInterpolateParams.end - colorInterpolateParams.start;
  let colorPoint: number = (colorInterpolateParams.end - value) / colorRange;
  if (colorInterpolateParams.reverse) colorPoint = 1 - colorPoint;
  return colorInterpolateParams.interpolateFunc(colorPoint);
}

export function hexToRgba(hex: string, alpha: number, asString: boolean): number[] | string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  const rgb = result ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16), alpha] : [0, 0, 0, alpha];
  return asString ? `rgba(${rgb.join(",")})` : rgb;
}

export function hexToRgb(hex: string, asString: boolean): number[] | string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  const rgb = result ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)] : [0, 0, 0];
  return asString ? `rgba(${rgb.join(",")})` : rgb;
}

function componentToHex(c: number): string {
  const hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

export function rgbToHex(r: number, g: number, b: number): string {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

export function rgbStringToHex(rgb: string): string {
  const nums = rgb.match(/\d+/g);
  if (nums === null) return "";
  const [r, g, b] = nums.map(num => parseInt(num));
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

export function  webglColor(color: string, opacity: number): number[] {
    const parsed = d3.color(color);
    if (parsed !== null) {
      const {r, g, b} = parsed.rgb();
      return [r / 255, g / 255, b / 255, opacity];
    }
    return [0, 0, 0, 1];
}

export function addAlphaToRGB(color: string, alpha: number): string {
  return color.replace("rgb", "rgba").replace(")", `, ${alpha})`)
}

export function hexToRGBA(hex: string, alpha: number) {
    const r = parseInt(hex.slice(1, 3), 16),
          g = parseInt(hex.slice(3, 5), 16),
          b = parseInt(hex.slice(5, 7), 16);

    return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
}

export function reduceSaturation(color: string): string {
  if (color === "gray") return "#e0e0e0"
  const c = new Color(color);
  c.lch.c *= 0.3;
  c.lch.l *= 1.4;
  return c.toString({format: "rgb"});
}