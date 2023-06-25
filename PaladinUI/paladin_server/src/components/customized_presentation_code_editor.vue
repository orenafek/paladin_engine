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
        />
  </div>
</template>

<script>
import Codemirror from "codemirror-editor-vue3";
import "codemirror/mode/javascript/javascript.js";
import "codemirror/theme/dracula.css";
import _ from "lodash";

export default {
  name: "CustomizedPresentationEditor",
  components: {Codemirror},
  emits: ['updateCustomizedCode'],
  methods: {
  },
  created() {
    this.debounceFn = _.debounce( () => {
      this.$emit('updateCustomizedCode', this.customized_data);
    }, 1000)
  },
  watch: {
    customized_data: {
        handler: function (val, oldVal) {
            this.debounceFn();
        }
    }
  },
  async mounted () {
    let customizationFile = await fetch('/static/customization.js');
    this.customized_data = await customizationFile.text();
    this.$emit('updateCustomizedCode', this.customized_data);
  },
  data: function() {
    return {
      customized_data: '',
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