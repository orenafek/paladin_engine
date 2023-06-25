<template>
  <div>
    <h3> Add a customized presentation: </h3>
    <p>
        Write customization functions for specific result types to change the appearance of your results.
    </p>
    <div v-for="(customization, index) in customizations" :key="index">
      <button @click="changeCustomizationClass(customization, index)">
        CustomizationClass-{{index}}
      </button>
    </div>
    <Codemirror
        v-model:value="customized_data"
        :options="codemirror_options"
        placeholder="Write your function here..."
        :height="200" :width="600" border
        @change="updateCustomizedCode"/>
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
    updateCustomizedCode: function() {
      this.debounceCustomizedCodeUpdate();
    },
    changeCustomizationClass: function(customization, index) {
      this.customized_data = customization;
      this.editor_index = index;
    }
  },
  created() {
    this.debounceCustomizedCodeUpdate = _.debounce( () => {
      this.customizations[this.editor_index] = this.customized_data;
      this.$emit('updateCustomizedCode', this.customizations);
    }, 1000)
  },
  async mounted () {
    let customizationFile = await fetch('/static/customization.js');
    this.customized_data = await customizationFile.text();
    this.customizations[this.editor_index] = this.customized_data;
    this.$emit('updateCustomizedCode', this.customizations);
  },
  data: function() {
    return {
      customizations: [''],
      customized_data: '',
      editor_index: 0,
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