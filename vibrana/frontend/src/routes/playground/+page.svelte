<script lang="ts">
  import { onMount } from 'svelte';
  import Graph from 'graphology';
  import Sigma from 'sigma';

  let container: HTMLDivElement;

  onMount(() => {
    const graph = new Graph();

    graph.addNode('1', {
      label: 'Node 1',
      x: 0,
      y: 0,
      size: 10,
      color: '#2563eb',
    });

    graph.addNode('2', {
      label: 'Node 2',
      x: 1,
      y: 1,
      size: 18,
      color: '#dc2626',
    });

    graph.addNode('3', {
      label: 'Node 3',
      x: 0.5,
      y: -0.7,
      size: 14,
      color: '#16a34a',
    });

    graph.addEdge('1', '2', { size: 4, color: '#7c3aed' });
    graph.addEdge('2', '3', { size: 3, color: '#0f172a' });
    graph.addEdge('3', '1', { size: 2, color: '#ea580c' });

    const renderer = new Sigma(graph, container);

    return () => {
      renderer.kill();
    };
  });
</script>

<svelte:head>
  <title>Sigma.js Playground</title>
</svelte:head>

<main class="min-h-screen bg-slate-50 p-6">
  <section class="mx-auto flex h-[calc(100vh-3rem)] max-w-6xl flex-col overflow-hidden rounded border border-slate-200 bg-white shadow-sm">
    <header class="border-b border-slate-200 px-5 py-4">
      <h1 class="text-lg font-semibold text-slate-950">Sigma.js basic graph</h1>
      <p class="mt-1 text-sm text-slate-600">A minimal Graphology graph rendered with Sigma.</p>
    </header>

    <div bind:this={container} class="min-h-0 flex-1" aria-label="Basic Sigma.js graph"></div>
  </section>
</main>
