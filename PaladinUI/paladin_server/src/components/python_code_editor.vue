<template>
  <Codemirror placeholder="Type your query here" :options="codemiror_options" @change="change" />
</template>

<script>
import Codemirror from "codemirror-editor-vue3";
import "codemirror/mode/python/python.js";
import "codemirror/theme/dracula.css";

export default {
  name: "PythonCodeEditor",
  components: {Codemirror},
  props: ['change'],
  data: function() {
    return {
      codemirror_options: {
        mode: "text/python",
        theme: "dracula",
        lineNumbers: false,
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