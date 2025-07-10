<script>
    import '../app.css';
    import {browser} from '$app/environment'
    import {QueryClient, QueryClientProvider} from '@tanstack/svelte-query'

    export let data;

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