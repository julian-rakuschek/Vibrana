<script lang="ts">

    import {Disclosure, DisclosureButton, DisclosurePanel} from "@rgossiaux/svelte-headlessui";
    import {Icon, ChevronDown} from "svelte-hero-icons";
    import {hexToRGBA} from "@lib/helper/colorHelper";

    export let header_text: string;
    export let bg_color: string = "#303f9f"
    export let bg_opacity: number = 0;
    export let classNames: string = "w-full"
</script>

<Disclosure class={classNames} let:open>
    <DisclosureButton class={`text-white ${open ? "rounded-t-lg" : "rounded-lg"} px-4 py-1 w-full flex flex-row justify-between items-center`} style={"background-color:" + bg_color}>
        {header_text}
        <Icon src="{ChevronDown}" solid class="w-7 h-7 text-white transition" style={open ? "transform: rotate(180deg);" : ""}/>
    </DisclosureButton>

    <DisclosurePanel class="gap-4 flex flex-col border-4 p-4 rounded-b-lg" style={`border-color: ${bg_color}; background-color: ${hexToRGBA(bg_color, bg_opacity)};`}>
         <slot />
    </DisclosurePanel>
</Disclosure>