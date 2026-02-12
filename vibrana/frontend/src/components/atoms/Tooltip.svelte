<script lang="ts">
    import Icon from "@iconify/svelte";

    interface Props {
        color: string;
        text: string;
    }

    let { color, text }: Props = $props();
</script>

<div class="group relative overflow-visible">
    <Icon icon="mingcute:question-line" width="20" height="20" style="color: {color}" />
    <div class="hidden absolute top-0 left-6 bg-white rounded-lg shadow-xl p-2 text-xs text-black/70 min-w-[200px] group-hover:block z-50">
        {text}
    </div>
</div>
