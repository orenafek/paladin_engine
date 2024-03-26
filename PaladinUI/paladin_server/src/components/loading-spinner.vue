<template>
  <button ref="btn" @click="submitAction" :style="{minWidth}">
    <span class="caption" :class="{isLoading}"><slot></slot></span>
    <spinner-anim v-if="isLoading"
      style="--size: 20px; display: inline-block; vertical-align: middle"/>
  </button>
</template>

<style scoped>
button {
  padding-top: 0;
  padding-bottom: 0;
  height: 23px;
}
span.caption.isLoading {
  display: none;
}
</style>

<script>
import SpinnerAnim from './spinner-anim.vue';

export default {
  name: "LoadingSpinner",
  props: {isLoading: Boolean},
  data: () => ({minWidth: undefined}),

  mounted() {
    this.minWidth = `${this.$refs.btn.getBoundingClientRect().width}px`;
  },

  methods: {
    async submitAction() {
      this.$emit('loadingButtonClick');
    }
  },

  components: { SpinnerAnim }
}
</script>