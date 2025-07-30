export function fillGaps(values: number[], empty_marker: number | null): (number | null)[] {
	const forward: (number | null)[] = values.slice();
	const backward: (number | null)[] = values.slice();
	const distances_forward: number[] = new Array(values.length).fill(Infinity);
	const distances_backward: number[] = new Array(values.length).fill(Infinity);

	let forward_memory = empty_marker;
	let backward_memory = empty_marker;
	let distances_forward_memory = -Infinity;
	let distances_backward_memory = Infinity;

	for (let i = 0; i < values.length; i++) {
		if (values[i] !== empty_marker) forward_memory = values[i];
		else if (forward_memory !== empty_marker) forward[i] = forward_memory;

		if (values[i] !== empty_marker) distances_forward_memory = i;
		else if (distances_forward_memory !== -Infinity) distances_forward[i] = i - distances_forward_memory;

		const inverse_i = values.length - i - 1;

		if (values[inverse_i] !== empty_marker) backward_memory = values[inverse_i];
		else if (backward_memory !== empty_marker) backward[inverse_i] = backward_memory;

		if (values[inverse_i] !== empty_marker) distances_backward_memory = inverse_i;
		else if (distances_backward_memory !== Infinity) distances_backward[inverse_i] =  distances_backward_memory - inverse_i;
	}

	const result: (number | null)[] = values.slice();
	for (let i = 0; i < values.length; i++) {
		if (values[i] === empty_marker) {
			result[i] = distances_forward[i] < distances_backward[i] ? forward[i] : backward[i];
		}
	}

	return result
}