import { interpolateSinebow } from 'd3';

export class ColorGenerator {
	protected colors: { [key: number]: string } = {"-1": "gray"};
	protected color_stops: number[] = [0];

	getColor(label: number): string {
		if (label === -1) return "gray";
		if (!this.colors[label]) {
			let color_stop = 0
			if (this.color_stops.length === 1) color_stop = 1;
			else if (this.color_stops.length > 1) {
				let max_diff = 0;
				let current_min_diff_pair: [number, number] | null = null;
				for (let i = 0; i < this.color_stops.length - 1; i++) {
					const diff = this.color_stops[i + 1] - this.color_stops[i];
					if (diff > max_diff || current_min_diff_pair === null) {
						max_diff = diff;
						current_min_diff_pair = [this.color_stops[i], this.color_stops[i + 1]];
					}
				}
				if (current_min_diff_pair) color_stop = (current_min_diff_pair[0] + current_min_diff_pair[1]) / 2;
			}
			this.color_stops.push(color_stop);
			this.color_stops.sort();
			this.colors[label] = interpolateSinebow(color_stop);
		}
		return this.colors[label];
	}

	getColorDictionary() {
		return this.colors;
	}

}