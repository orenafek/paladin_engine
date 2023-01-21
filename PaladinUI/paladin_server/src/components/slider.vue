<template>
  <div>
    <Slider :min="minV" :max="maxV" @change="sliderChange" />
  </div>
</template>

<script>
import Slider from '@vueform/slider'

export default {
  props: ['minV', 'maxV', 'sliderChange'],
  components: {
    Slider,
  },
  // data: () => ({
  //   minV: this.min,
  //   maxV: this.max
  // })
}
</script>

<style src="@vueform/slider/themes/default.css"></style>