import { dispatch } from 'd3-dispatch';
import { pointer } from 'd3-selection';
import { rebind } from '@d3fc/d3fc-rebind';

// extended from https://github.com/d3fc/d3fc/blob/master/packages/d3fc-pointer/src/pointer.js
// the original d3fc implementation was missing a click event handler
export default function betterPointer(): unknown {
    const pointEvent = dispatch('point', 'click');

    function mousemove(event) {
        const point = pointer(event);
        pointEvent.call('point', this, [{ x: point[0], y: point[1] }]);
    }

    function mouseleave() {
        void pointEvent.call('point', this, []);
    }

    function mouseclick(event) {
        const point = pointer(event);
        pointEvent.call('click', this, [{ x: point[0], y: point[1] }]);
    }

    const instance = (selection) => {
        selection
            .on('mouseenter.pointer', mousemove)
            .on('mousemove.pointer', mousemove)
            .on('mouseleave.pointer', mouseleave)
            .on('click.pointer', mouseclick);
    };

    rebind(instance, pointEvent, 'on');

    return instance;
};