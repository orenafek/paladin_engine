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
    time_ranges() {
      return Object.keys(Object.values(this.sortedEntries)[0]);
    },

    headline() {
      return Object.keys(this.sortedEntries);
    },


  },
  methods: {
    isEmpty: o => JSON.stringify(o) === "{}",
    result(key_index, range_index) {
      return Object.values(Object.values(this.sortedEntries)[key_index])[range_index];
    }
  }
}

</script>

<style scoped>
table, th, thead, td {
  border: 1px solid;
}
</style>