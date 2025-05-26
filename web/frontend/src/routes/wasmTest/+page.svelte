<script lang="ts" type="module">
	import createPCA from './pca.js';
	import { onMount } from 'svelte';

	onMount(async () => {
		const PCA = await createPCA();

		// Create a new C++ vector<double> from the JS array
		const vec = new PCA.VectorDouble();
		[1, 2, 3, 4].forEach(val => vec.push_back(val));

		// Now call the function
		const res = PCA.dummy(vec);
		console.log(res);

// // Input data: rows are samples
// 		const data = [
// 			[2.5, 2.4],
// 			[0.5, 0.7],
// 			[2.2, 2.9],
// 			[1.9, 2.2],
// 			[3.1, 3.0]
// 		];
//
// // Get principal components
// 		const [pc1, pc2] = PCA.getPrincipalComponents(data);
// 		console.log('PC1:', pc1);
// 		console.log('PC2:', pc2);
//
// // Project data onto PC1, PC2
// 		const projected = PCA.project(pc1, pc2, data);
// 		console.log('Projected Data:', projected);
	});


</script>

<p>Hi WASM</p>