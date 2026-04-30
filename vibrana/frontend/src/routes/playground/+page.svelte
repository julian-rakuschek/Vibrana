<script lang="ts">

  import PeriodogramBar from "@components/differenceView/PeriodogramBar.svelte";
  import DifferenceBand from "@components/differenceView/DifferenceBand.svelte";

  let periodogram1: number[] = [0, 0, 10, 20, 10, 0, 0, 0, 40, 0];
  let periodogram2: number[] = [0, 0, 10, 20, 10, 0, 20, 30, 10, 0];

  const global_max = Math.max(...periodogram1, ...periodogram2);

</script>

<div class="flex flex-col">
  <PeriodogramBar color_bg={"#f06292"} color_fg={"#ad1457"} periodogram={periodogram1} global_max={global_max} />
  <DifferenceBand periodogram1={periodogram1} periodogram2={periodogram2} global_max={global_max} />
  <PeriodogramBar color_bg={"#a5d6a7"} color_fg={"#2e7d32"} periodogram={periodogram2} global_max={global_max} />
</div>
