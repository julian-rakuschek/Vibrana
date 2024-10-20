<script lang="ts">

    import {Disclosure, DisclosureButton, DisclosurePanel} from "@rgossiaux/svelte-headlessui";
    import {Icon, ChevronDown} from "svelte-hero-icons";

    export let header_text: string;
</script>

<Disclosure class="w-full" let:open>
    <DisclosureButton class={`bg-indigo-700 text-white ${open ? "rounded-t-lg" : "rounded-lg"} px-4 py-1 w-full flex flex-row justify-between items-center`}>
        {header_text}
        <Icon src="{ChevronDown}" solid class="w-7 h-7 text-white transition" style={open ? "transform: rotate(180deg);" : ""}/>
    </DisclosureButton>

    <DisclosurePanel class="gap-4 flex flex-col border-indigo-700 border-2 p-4 rounded-b-lg ">
         <slot />
    </DisclosurePanel>
</Disclosure>