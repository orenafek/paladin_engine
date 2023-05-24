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
    customization: String,
  },
  methods: {
    result(rowKey, colKey) {
      let item_to_print = this.value.rowData[rowKey]?.[colKey];
      let body = this.customization;
      let wrap = s => "{ return " + body + " };" //return the block having function expression
      let func = new Function( wrap(body) );
      let customized_item = func.call( null ).call(null, item_to_print); //invoke the function using arguments
      return customized_item;
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