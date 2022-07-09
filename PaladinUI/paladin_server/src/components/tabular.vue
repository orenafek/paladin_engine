<template>
  <table v-if="!isEmpty(sortedEntries)">
    <thead>
    <td> Time Range</td>
    <td v-for="h in headline"> {{ h }}</td>
    </thead>
    <tr v-for="entry in Object.entries(sortedEntries)">
      <td> {{ entry[0] }}</td>
      <td v-for="result in entry[1][0]"> {{ result }}</td>
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
    headline() {
      if (this.isEmpty(this.sortedEntries)) {
        return [];
      }

      /* Each result is in the format:
           (from, to): [{<result(null/real)>, <replacements>}, <result(null/real)>, replacement>,...}]
      */
      const firstResultValue = Object.entries(this.sortedEntries)[0][1][0];
      return Object.keys(firstResultValue);
    }
  },
  methods: {
    isEmpty: o => JSON.stringify(o) === "{}",
  }
}

</script>

<style scoped>
table, th, thead, td {
  border: 1px solid;
}
</style>