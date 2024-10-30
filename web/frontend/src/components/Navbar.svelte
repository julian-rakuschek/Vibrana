<script lang="ts">
    import {Icon, Bars3, XMark} from "svelte-hero-icons";
    import {goto} from '$app/navigation';
    import {getContext} from "svelte";

    export let darkMode = false; // Default to light mode

    let mobileMenuOpen = false;

    const menuLinks = [
        {name: "Introduction", link: "/intro"},
        {name: "Datasets", link: "/datasets"},
        {name: "Authors", link: "/authors"}
    ];

    function toggleMobileMenu() {
        mobileMenuOpen = !mobileMenuOpen;
    }

    function closeMobileMenu() {
        mobileMenuOpen = false;
    }

    function navigateTo(link: string) {
        goto(link);
        closeMobileMenu();
    }

    const {ro} = getContext("ro") as { ro: boolean }
</script>

<header class={`${darkMode ? 'bg-[#0e1b40]' : 'bg-white'} z-50`}>
    <nav class="mx-auto flex items-center justify-between py-4 px-6 lg:px-8" aria-label="Global">
        <div class="flex lg:flex-1">
            <a href="/" class="-m-1.5 p-1.5 flex flex-row flex-nowrap gap-4 items-center">
                <img width="50" alt="Vibrana" src="/vibrana.png"/>
                <span class={`${darkMode ? 'text-white' : 'text-black'} font-bold text-2xl`}>Vibrana</span>
            </a>
        </div>

        <div class="flex flex-row gap-5 lg:hidden">
            <div class="flex lg:flex-1 lg:justify-end gap-x-4">
                {#if ro}
                    <div class="bg-[#304ffe] text-white rounded-lg px-4 py-2 text-sm">
                        Read-Only Mode
                    </div>
                {/if}
            </div>
            <button
                    type="button"
                    class="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
                    on:click={toggleMobileMenu}
            >
                <span class="sr-only">Open main menu</span>
                <Icon src="{Bars3}" class="h-6 w-6" aria-hidden="true"/>
            </button>
        </div>
        <div class="hidden lg:flex lg:gap-x-12">
            {#each menuLinks as menuLink}
                <a href={menuLink.link} class={`text-sm font-semibold leading-6 ${(darkMode) ? "text-white before:border-b-white" : "text-gray-900 before:border-b-indigo-700"} border-animation`}>
                    {menuLink.name}
                </a>
            {/each}
        </div>
        <div class="hidden lg:flex lg:flex-1 lg:justify-end gap-x-4">
            {#if ro}
                <div class="bg-[#304ffe] text-white rounded-lg px-4 py-2 text-sm">
                    Read-Only Mode
                </div>
            {/if}
        </div>
    </nav>

    <!-- Mobile Menu -->
    {#if mobileMenuOpen}
        <div class="lg:hidden fixed inset-0 z-10 bg-black opacity-50" on:click={closeMobileMenu}></div>
        <div class={`fixed inset-y-0 right-0 z-50 w-full overflow-y-auto ${darkMode ? 'bg-[#0e1b40]' : 'bg-white'} px-6 py-6 sm:max-w-sm`}>
            <div class="flex items-center justify-between">
                <a href="/" class="-m-1.5 p-1.5">
                    <span class={`${darkMode ? 'text-white' : 'text-black'} font-bold text-2xl`}>Vibrana</span>
                </a>
                <button
                        type="button"
                        class="-m-2.5 rounded-md p-2.5 text-gray-700"
                        on:click={toggleMobileMenu}
                >
                    <span class="sr-only">Close menu</span>
                    <Icon src="{XMark}" class="h-6 w-6" aria-hidden="true"/>
                </button>
            </div>
            <div class="mt-6 flow-root">
                <div class="-my-6 divide-y divide-gray-500/10">
                    <div class="space-y-2 py-6">
                        {#each menuLinks as menuLink}
                            <a
                                    href={menuLink.link}
                                    class={`-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 ${darkMode ? 'text-white' : 'text-gray-900'}`}
                                    on:click={() => navigateTo(menuLink.link)}
                            >
                                {menuLink.name}
                            </a>
                        {/each}
                    </div>
                </div>
            </div>
        </div>
    {/if}
</header>
