<script lang="ts">
    import {Jumper} from 'svelte-loading-spinners';

    export let color: string = "#304ffe";
</script>
<div class="w-full h-full flex align-middle justify-center items-center justify-items-center">
    <Jumper {color} />
</div>