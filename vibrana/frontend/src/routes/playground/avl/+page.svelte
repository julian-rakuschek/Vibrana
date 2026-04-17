<script lang="ts">
    import {density1d} from 'fast-kde';

    // const sample = [1,1,4,4,4,4,4,7,7];
    const sample = [7,7];
    const densities = density1d(sample, {bins: 10, extent: [5, 7], bandwidth: 3}).grid();
    console.log(densities)
</script>
