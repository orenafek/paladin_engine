<template>
    <div class="semipolar-spinner" style="--nrings: 4; --time-shift: 0.05">
        <div class="ring"></div>
        <div class="ring"></div>
        <div class="ring"></div>
        <div class="ring"></div>
    </div>
</template>

<style src="./epic-spinners.css"></style>

<script lang="ts">
import {Component, toNative, Vue} from "vue-facing-decorator";

@Component
class SpinnerAnim extends Vue {

}

export default toNative(SpinnerAnim);
</script>