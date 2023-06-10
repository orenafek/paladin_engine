<template>
  <div v-if="this.contentData.contentType==='text/plain'" v-text="this.contentData.content"></div>
  <div v-else-if="this.contentData.contentType==='text/html'" v-html="this.contentData.content"></div>
  <div v-else>UNABLE TO PARSE DATA</div>
</template>

<script>
export default {
  name: "CustomizedPresentationView",
  props: {
    contentData: Object,
  },
}
</script>

<style scoped>

</style>