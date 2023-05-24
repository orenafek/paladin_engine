<template>
  <div>
    <h3> Add a customized presentation: </h3>
    <p>
        Write customization functions for specific result types to change the appearance of your results.
    </p>
      <Codemirror
        v-model:value="customized_data"
        :options="codemirror_options"
        placeholder="Write your function here..."
        :height="200" :width="600" border
        @change="updateCustomizedCode()"/>
  </div>
</template>

<script>
import Codemirror from "codemirror-editor-vue3";
import "codemirror/mode/javascript/javascript.js";
import "codemirror/theme/dracula.css";

export default {
  name: "CustomizedPresentation",
  components: {Codemirror},
  emits: ['updateCustomizedCode'],
  methods: {
    updateCustomizedCode() {
      this.$emit('updateCustomizedCode', this.customized_data)
    }
  },
  data: function() {
    return {
      customized_data: 'function (data) {\n' +
          '  return data;\n' +
          '}',
      codemirror_options: {
        mode: "text/javascript",
        theme: "dracula",
        lineNumbers: true,
        smartIndent: true,
        indentUnit: 2,
        foldGutter: true,
        styleActiveLine: true
      }
    }
  }
}
</script>

<style scoped>

</style>