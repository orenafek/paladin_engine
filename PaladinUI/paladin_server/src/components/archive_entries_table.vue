<script>
import {capitalizeFirstLetter} from "../string_utils";
import Highlighted from "./highlighted.vue";

export default {
  name: "ArchiveTable",
  props: {entries: Array},
  components: {highlighted: Highlighted},
  compilerOptions: {
    delimiters: ['$$[', ']$$']
  },
  methods:{
    capitalizeFirstLetter
  }
}
</script>

<template>
  <table style="max-width: 400px;">
    <tr>
      <td v-if="entries.length > 0"
          v-for="k in Object.keys(entries[0])" v-html="capitalizeFirstLetter(k)"/>
    </tr>
    <tr v-for="entry in entries">
      <td v-for="value, key in entry">
        <highlighted :code="value" />
      </td>
    </tr>
  </table>
</template>


<style scoped>

</style>