<template>
  <v-runtime-template :template="formattedDataTemplate"></v-runtime-template>
</template>

<script>
import VRuntimeTemplate from "vue3-runtime-template";

export default {
  name: "CustomizedPresentationView",
  props: {
    contentType: String,
    content: [Object, String],
    data: Object,
  },
  components: {
    VRuntimeTemplate
  },
  computed: {
    formattedDataTemplate() {
      if (this.contentType === 'text/plain') {
        return '<span>{{this.content}}</span>';
      }
      if (this.contentType === 'text/html') {
        return this.content;
      }
      return '<span>UNABLE TO PARSE DATA</span>';
    }
  }
}
</script>

<style scoped>

</style>