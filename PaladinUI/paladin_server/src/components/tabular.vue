<template>
  <table v-if="value?.columnHeaders">
    <thead>
      <td>Time</td>
      <td v-for="h in value.columnHeaders"> {{ h }}</td>
    </thead>
    <tr v-for="rowHead in value.rowHeaders">
      <td @click="rowSelect($event, rowHead)"> {{ rowHead.display }}</td>
      <td v-for="colKey in value.columnHeaders">
        <customized-presentation-view v-bind="result(rowHead.key, colKey)"></customized-presentation-view>
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
    customization: String,
  },
  methods: {
    result(rowKey, colKey) {
      let item = this.value.rowData[rowKey]?.[colKey];
      let formattedData = {"contentType": "text/plain", "content": item};
      try {
        let customizationClass = eval('(' + this.customization + ')');
        if (customizationClass.matches(item)) {
          formattedData = customizationClass.getFormattedData(item);
        }
      }
      catch(error) {
        console.log("Error: " + error);
      }
      // Add the item itself to the formatted-data object, to allow the user to access it in the view template
      formattedData.data = item;

      return formattedData;
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