<template>
  <table v-if="value?.columnHeaders">
    <thead>
    <td>Time</td>
    <td v-for="h in value.columnHeaders"> {{ h }}</td>
    </thead>
    <tr v-for="rowHead in value.rowHeaders">
      <td @click="rowSelect($event, rowHead)"> {{ rowHead.display }}</td>
      <td v-for="colKey in value.columnHeaders"> {{ result(rowHead.key, colKey) }}</td>
    </tr>
  </table>
</template>

<script>
export default {
  name: "tabular",
  props: {
    value: Object,
  },
  methods: {
    result(rowKey, colKey) {
      return this.value.rowData[rowKey]?.[colKey];
    },
    rowSelect($event, rowHead) {
      this.$emit('row:select', {$event, rowHead});
    }
  }
}

</script>

<style scoped>
table, th, thead, td {
  border: 1px solid;
}
</style>