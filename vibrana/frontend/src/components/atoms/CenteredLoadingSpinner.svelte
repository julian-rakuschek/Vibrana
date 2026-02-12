<script lang="ts">
    import {Jumper} from 'svelte-loading-spinners';

    interface Props {
        color?: string;
    }

    let { color = "#304ffe" }: Props = $props();
</script>
<div class="w-full h-full flex align-middle justify-center items-center justify-items-center">
    <Jumper {color} />
</div>