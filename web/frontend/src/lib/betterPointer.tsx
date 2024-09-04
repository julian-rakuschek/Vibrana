import { dispatch } from 'd3-dispatch';
import { pointer } from 'd3-selection';
import { rebind } from '@d3fc/d3fc-rebind';
import * as d3 from "d3";

// extended from https://github.com/d3fc/d3fc/blob/master/packages/d3fc-pointer/src/pointer.js
// the original d3fc implementation was missing a click event handler
export default function betterPointer(): unknown {
    const pointEvent = dispatch('point', 'click');

    function mousemove(event) {
        const point = pointer(event);
        pointEvent.call('point', this, [{ x: point[0], y: point[1], buttons: event.buttons }]);
    }

    function mouseleave() {
        void pointEvent.call('point', this, []);
    }

    function mouseclick(event, button?: number) {
        const point = pointer(event);
        pointEvent.call('click', this, [{ x: point[0], y: point[1], buttons: button ? button : 1 }]);
    }

    const instance = (selection) => {
        selection
            .on('mouseenter.pointer', mousemove)
            .on('mousemove.pointer', mousemove)
            .on('mouseleave.pointer', mouseleave)
            .on('click.pointer', mouseclick)
            .on("contextmenu", function (event, i) {
           event.preventDefault();
           mouseclick(event, 2)
           // react on right-clicking
        })
    };

    rebind(instance, pointEvent, 'on');

    return instance;
};