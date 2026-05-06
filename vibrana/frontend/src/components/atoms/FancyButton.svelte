<script lang="ts">
	import { Icon, type IconSource } from 'svelte-hero-icons';



	const primary_class_string = `
		flex justify-center px-2 items-center h-full w-full button bg-indigo-600 rounded-lg cursor-pointer select-none
    active:translate-y-1  active:[box-shadow:0_0px_0_0_#3949ab,0_0px_0_0_#3949ab41]
    active:border-b-[0px]
    transition-all duration-150 [box-shadow:0_6px_0_0_#3949ab,0_6px_0_0_#3949ab41]
    border-b-[1px] border-indigo-600
	`;

	const danger_class_string = `
		flex justify-center px-2 items-center h-full w-full button bg-red-500 rounded-lg cursor-pointer select-none
    active:translate-y-1  active:[box-shadow:0_0px_0_0_#e53935,0_0px_0_0_#c6282841]
    active:border-b-[0px]
    transition-all duration-150 [box-shadow:0_6px_0_0_#e53935,0_6px_0_0_#c6282841]
    border-b-[1px] border-red-500
	`;

	interface Props {
		button_color?: "danger" | "primary";
		disabled?: boolean;
		icon?: IconSource | undefined;
		text?: string;
		text_size?: string;
	}

	let {
		button_color = "primary",
		disabled = false,
		icon = undefined,
		text = "",
		text_size = "text-lg"
	}: Props = $props();
</script>


<div class={`${button_color === "primary" ? primary_class_string : danger_class_string} ${disabled ? "opacity-50 cursor-not-allowed pointer-events-none" : ""}`}>
	{#if icon}<Icon src="{icon}" class="w-7 h-7 text-white" solid/>{/if}
	{#if text !== ""}<span class={`flex flex-col justify-center items-center h-full text-white font-semibold ${text_size} mx-3`}>{text}</span>{/if}
</div>
