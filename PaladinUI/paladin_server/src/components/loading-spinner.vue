<template>
    <button ref="btn" @click="submitAction" :style="{minWidth}">
        <span class="caption" :class="{isLoading}"><slot></slot></span>
        <spinner-anim v-if="isLoading"
                      style="--size: 20px; display: inline-block; vertical-align: middle"/>
    </button>
</template>


<script lang="ts">

import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import SpinnerAnim from "./spinner-anim.vue";

@Component({
    components: {SpinnerAnim}
})
class LoadingSpinner extends Vue {
    @Prop isLoading: Boolean

    $refs: {btn: HTMLButtonElement}

    minWidth: string = ''
    mounted() {
        this.minWidth = `${this.$refs.btn.getBoundingClientRect().width}px`;
    }

    async submitAction() {
        this.$emit('loadingButtonClick');
    }

}

export default toNative(LoadingSpinner);
</script>

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
