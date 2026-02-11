<script lang="ts">
    import './layout.css';
    import {browser} from '$app/environment'
    import {QueryClient, QueryClientProvider} from '@tanstack/svelte-query'
    import type {Config} from "@lib/types";

    export let data: Config;

    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                enabled: browser,
            },
        },
    })
</script>

<QueryClientProvider client={queryClient}>
    <div class="w-full h-full flex flex-col">
        <slot/>
    </div>
</QueryClientProvider>