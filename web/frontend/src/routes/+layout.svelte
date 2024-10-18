<script>
    import '../app.css';
    import {browser} from '$app/environment'
    import {QueryClient, QueryClientProvider} from '@tanstack/svelte-query'
    import {setContext} from "svelte";
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                enabled: browser,
            },
        },
    })
    sessionStorage.normals = JSON.stringify({})
    sessionStorage.labels = JSON.stringify([])

    /** @type {import('./$types').PageData} */
    export let data;

    setContext("ro", {ro: data.ro})
</script>

<QueryClientProvider client={queryClient}>
    <div class="w-full">
        <slot/>
    </div>
</QueryClientProvider>