<script lang="ts">
    import {useQueryFetch} from "@lib/api/ApiQueries";
    import {ApiRoutes} from "@lib/api/ApiRoutes";

    interface Props {
        dataset: string;
        subset: string;
    }

    let { dataset, subset }: Props = $props();

</script>

<p>TODO Coverage</p>