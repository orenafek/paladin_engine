<template>
  <table v-if="!isEmpty(sortedEntries)">
    <thead>
    <td> Time Range</td>
    <td v-for="h in headline"> {{ h }}</td>
    </thead>
    <tr v-for="i in time_ranges.length">
      <td> {{ time_ranges[i - 1] }}</td>
      <td v-for="k in headline.length"> {{ result(i - 1, k - 1) }}</td>
    </tr>
  </table>
</template>

<script>
export default {
  name: "tabular",
  props: {
    value: Object,
  },
  computed: {
    sortedEntries() {
      return this.isEmpty(this.value) ? {} : JSON.parse(this.value);
    },

    headlineIndex() {
      return Object.keys(this.sortedEntries).indexOf('keys')
    },

    headline() {
      return Object.values(this.sortedEntries)[this.headlineIndex];
    },

    time_ranges() {
      const allKeys = Object.keys(this.sortedEntries);

      /* Remove keys index. */
      allKeys.splice(this.headlineIndex, 1);

      return allKeys;
    },

  },
  methods: {
    isEmpty: o => JSON.stringify(o) === "{}",
    result(range_index, key_index) {
      return Object.values(Object.values(this.sortedEntries)[range_index])[key_index];
    }
  }
}

</script>

<style scoped>
table, th, thead, td {
  border: 1px solid;
}
</style>