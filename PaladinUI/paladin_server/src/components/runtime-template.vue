<template>
    <v-runtime-template :template="wrapTemplate"></v-runtime-template>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";


@Component
class RuntimeTemplate extends Vue {

    @Prop template?: Template


    wrapTemplate() {
        if (this.template.type === 'text/plain') {
            return '<span>{{this.content}}</span>';
        }
        if (this.template.type === 'text/html') {
            return this.template.content;
        }

        return '<span>{{this.data}}</span>';
    }
}

export {FormattedData};
export default toNative(RuntimeTemplate);

</script>

<style scoped>

</style>