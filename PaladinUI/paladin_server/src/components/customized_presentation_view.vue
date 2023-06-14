<template>
  <span v-if="this.contentData === null"></span>
  <span v-else-if="this.contentData?.contentType==='text/plain'" v-text="this.contentData?.content"></span>
  <span v-else-if="this.contentData?.contentType==='text/html'" v-html="this.contentData?.content"></span>
  <span v-else>UNABLE TO PARSE DATA</span>
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