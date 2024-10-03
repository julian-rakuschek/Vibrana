<script>
    import '../app.css';
    import {browser} from '$app/environment'
    import {QueryClient, QueryClientProvider} from '@tanstack/svelte-query'

    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                enabled: browser,
            },
        },
    })
</script>

<QueryClientProvider client={queryClient}>
    <div class="w-full h-full absolute top-0 flex flex-col">
        <slot/>
    </div>
</QueryClientProvider>