<template>
  <div>
    <h3> Add a customized presentation: </h3>
    <p>
        Write customization functions for specific result types to change the appearance of your results.
    </p>
    <div class="customized-presentation">
      <ul class="tab">
        <li v-for="(customization, index) in customizations" :key="index">
          <button @click="changeCustomizationClass(customization, index)" :class="{'selected-button': index === this.editor_index}">
            CustomizationClass-{{index}}
          </button>
        </li>
        <li>
          <button @click="addCustomizationClass">+</button>
        </li>
      </ul>
      <Codemirror class="code-mirror"
          v-model:value="customized_data" :options="codemirror_options"
          @change="updateCustomizedCode"/>
    </div>
    <div class="errors" v-show="presentable_error.length > 0">{{presentable_error}}</div>
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
  props: {
      customization_error: String,
  },
  emits: ['updateCustomizedCode'],
  methods: {
    updateCustomizedCode: function() {
      this.debounceCustomizedCodeUpdate();
    },
    changeCustomizationClass: function(customization, index) {
      this.customized_data = customization;
      this.editor_index = index;
    },
    addCustomizationClass: async function() {
      this.editor_index = this.customizations.length;
      this.customized_data = await this.fetchCustomizationClass();
      this.customizations[this.editor_index] = this.customized_data;
    },
    fetchCustomizationClass: async function() {
      let customizationFile = await fetch('/static/customization.js');
      return await customizationFile.text();
    }
  },
  created() {
    this.debounceCustomizedCodeUpdate = _.debounce( () => {
      this.presentable_error = '';
      this.customizations[this.editor_index] = this.customized_data;
      this.$emit('updateCustomizedCode', this.customizations);
    }, 1000)
  },
  async mounted () {
    this.customized_data = await this.fetchCustomizationClass();
    this.customizations[this.editor_index] = this.customized_data;
    this.$emit('updateCustomizedCode', this.customizations);
  },
  watch: {
    customization_error: function (val, oldVal) {
      this.presentable_error = val;
    }
  },
  data: function() {
    return {
      customizations: [''],
      customized_data: '',
      editor_index: 0,
      presentable_error: '',
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
ul {
  list-style-type: none; /* Remove bullets */
  padding: 0;
  margin: 0;
}

ul li {
  border: 1px solid #ddd; /* Add a thin border to each list item */
  margin-top: -1px; /* Prevent double borders */
  background-color: #192f9a;
}

.customized-presentation {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: left;
}

.code-mirror {
  height: 300px;
  width: 700px;
  border: 1px solid;
}

.tab button {
  background-color: inherit;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 4px 6px;
  transition: 0.3s;
  width: 100%;
  color: white;
}

.tab button:hover {
  background-color: #6b6ed5;
}

.tab button.selected-button {
  background-color: #7195e0;
}

.errors {
  color: orangered;
  padding: 10px;
}
</style>