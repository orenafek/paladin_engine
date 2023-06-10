<template>
  <table v-if="value?.columnHeaders">
    <thead>
    <td>Time</td>
    <td v-for="h in value.columnHeaders"> {{ h }}</td>
    </thead>
    <tr v-for="rowHead in value.rowHeaders">
      <td @click="rowSelect($event, rowHead)"> {{ rowHead.display }}</td>
      <td v-for="colKey in value.columnHeaders">
        <customized-presentation-view :content-data="result(rowHead.key, colKey)"></customized-presentation-view>
      </td>
    </tr>
  </table>
</template>

<script>
import CustomizedPresentationView from "./customized_presentation_view.vue";

export default {
  name: "tabular",
    components: {customizedPresentationView: CustomizedPresentationView},
    props: {
    value: Object,
    matches: String,
    format: String,
  },
  methods: {
    result(rowKey, colKey) {
      let item = this.value.rowData[rowKey]?.[colKey];
      let hasMatch = applyStringFunctionToItem(this.matches, item);
      if (hasMatch) {
          item = applyStringFunctionToItem(this.format, item);
      }
      return item;
    },
    rowSelect($event, rowHead) {
      this.$emit('row:select', {$event, rowHead});
    }
  }
}

const applyStringFunctionToItem = function(body, item) {
  let wrap = s => "{ return " + body + " };" //return the block having function expression
  let func = new Function( wrap(body) );
  let result = func.call( null ).call(null, item); //invoke the function using arguments
  return result;
}

</script>

<style scoped>
table, th, thead, td {
  border: 1px solid;
}
</style>