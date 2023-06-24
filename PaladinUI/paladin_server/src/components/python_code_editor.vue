<template>
  <Codemirror placeholder="Type your query here" :options="codemirror_options" v-model:value="value"></Codemirror>
</template>

<script>
import Codemirror from "codemirror-editor-vue3";
import "codemirror/mode/python/python.js";
import "codemirror/theme/dracula.css";
import {bracketMatching} from "@codemirror/matchbrackets";

export default {
  name: "PythonCodeEditor",
  components: {Codemirror},
  props: ['value'],
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
  },
  extensions: [
      bracketMatching({brackets: "(){}[]"})
  ]
}
</script>

<style scoped>

</style>