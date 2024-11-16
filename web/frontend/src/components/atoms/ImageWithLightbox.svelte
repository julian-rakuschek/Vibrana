<script lang="ts">
    import {scale, fade} from 'svelte/transition';

    export let src: string;
    export let alt: string;
    export let classNames: string;

    let open = false;
</script>

<img src={src} alt={alt} class={classNames} on:click={() => open = true}/>

{#if open}
    <div class="fixed w-full h-full top-0 left-0 bg-black/20 z-50 grid place-items-center"
         transition:fade={{duration: 200}} on:click={() => open = false}>
        <img src={src} alt={alt} class="bg-white p-4 rounded-lg object-contain h-2/3 w-2/3"
             transition:scale={{duration: 300}}/>
    </div>
{/if}