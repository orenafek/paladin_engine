<template>
  <v-runtime-template :template="formattedDataTemplate"></v-runtime-template>
</template>

<script>
import VRuntimeTemplate from "vue3-runtime-template";

export default {
  name: "CustomizedPresentationView",
  props: {
    formattedData: Object,
  },
  components: {
    VRuntimeTemplate
  },
  computed: {
    formattedDataTemplate() {
      if (this.formattedData === null) {
          return '<span></span>';
      }
      if (this.formattedData?.contentType==='text/plain') {
        return '<span>{{this.formattedData?.content}}</span>';
      }
      if (this.formattedData?.contentType==='text/html') {
        return this.formattedData?.content;
      }

      return '<span>UNABLE TO PARSE DATA</span>';
    }
  }
}
</script>

<style scoped>

</style>