<script>
    export let query;
</script>


{#if $query.isPending}
  <p>Loading...</p>
{/if}

{#if $query.error}
  <p>An error has occurred: {$query.error.message}</p>
{/if}

{#if $query.isSuccess}
  <slot />
{/if}