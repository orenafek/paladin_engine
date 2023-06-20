<template>
  <table v-if="value?.columnHeaders">
    <thead>
    <td>Time</td>
    <td v-for="h in value.columnHeaders"> {{ h }}</td>
    </thead>
    <tr v-for="rowHead in value.rowHeaders">
      <td @click="rowSelect($event, rowHead)"> {{ rowHead.display }}</td>
      <td v-for="colKey in value.columnHeaders">
        <customized-presentation-view :formatted-data="result(rowHead.key, colKey)"></customized-presentation-view>
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
    customization: String,
  },
  methods: {
    result(rowKey, colKey) {
      let item = this.value.rowData[rowKey]?.[colKey];
      let classString = '(' + this.customization + ')';
      let customizationClass = eval(classString);
      let hasMatch = customizationClass.matches(item);
      if (hasMatch) {
          item = customizationClass.getFormattedData(item);
      }
      return item;
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