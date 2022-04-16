<template>
  <table style="max-width: 400px;">
    <thead>
    <td v-if="entries.length > 0"
        v-for="k in Object.keys(entries[0])" v-html="capitalizeFirstLetter(k)"/>
    </thead>
    <tr v-for="entry in entries">
      <td v-for="value, key in entry">
            <highlighted :code="value"></highlighted>
      </td>
    </tr>
  </table>
</template>

<script>
import {capitalizeFirstLetter} from "../string_utils";


export default {
  name: "entries_table",
  props: ['entries']
}
</script>

<style scoped>

</style>