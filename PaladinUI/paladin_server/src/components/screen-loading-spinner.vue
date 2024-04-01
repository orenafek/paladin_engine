<template>
    <div class="entire-screen-loading-spinner" >
        <spinner-anim/>
    </div>
</template>

<script lang="ts">
import {Component, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import SpinnerAnim from "./spinner-anim.vue";

@Component({
    components: {SpinnerAnim}
})
class ScreenLoadingSpinner extends Vue {

}

export default toNative(ScreenLoadingSpinner);

</script>

<style lang="scss" scoped>
.entire-screen-loading-spinner {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3); /* semi-transparent black */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999; /* ensure it's above other content */
}
</style>
