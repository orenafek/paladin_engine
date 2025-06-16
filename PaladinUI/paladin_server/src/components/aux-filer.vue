<template>
    <input id="aux_file" type="file">
    <loading-spinner :is-loading="auxFileSending" @loading-button-click="sendAuxFile">
        Send Aux File
    </loading-spinner>
</template>

<script lang="ts">
import {Component, toNative, Vue} from "vue-facing-decorator";

// @ts-ignore
import LoadingSpinner from "./loading-spinner.vue";

import {upload} from '../request';

@Component({components: {LoadingSpinner}})
class AuxFiler extends Vue {

    auxFileSending: boolean = false

    async sendAuxFile() {
        const aux_file_input = document.getElementById("aux_file") as HTMLInputElement;
        if (aux_file_input.files.length > 0) {
            try {
                this.auxFileSending = true;
                await upload(aux_file_input.files[0], "/uploader");
            } finally {
                this.auxFileSending = false;
            }
        }
    }
}

export default toNative(AuxFiler);

</script>

<style lang="scss" scoped>

</style>