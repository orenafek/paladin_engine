<template>
  <form @submit.prevent="submitAction" class="vld-parent" ref="formContainer">
    <button type="submit">{{ submit_button_text }}</button>
  </form>
</template>

<script>
import {ref} from 'vue';
// Import the method.
import {useLoading} from 'vue3-loading-overlay';
// Import stylesheet
import 'vue3-loading-overlay/dist/vue3-loading-overlay.css';
// Init plugin

export default {
  name: "LoadingSpinner",
  props: {submit_button_text: String, is_loaded: Boolean},
  watch: {
    is_loaded(newVal, oldVal) {
      if (newVal) {
        this.loader.hide();
      }
    }
  },
  setup() {
    let fullPage = ref(true);
    let formContainer = ref(null);
    let loader = ref(useLoading());
    return {
      fullPage,
      formContainer,
      loader
    }
  },

  methods: {

    async submitAction() {
      this.loader.show({
        // Optional parameters
        container: this.fullPage ? null : this.formContainer.value,
        canCancel: false,
      });
      this.$emit('loadingButtonClick');
    }
  }

}
</script>