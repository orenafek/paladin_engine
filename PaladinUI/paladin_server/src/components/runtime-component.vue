<template>
    <div v-if="type === 'text/html'">
        <v-runtime-template :template="content"></v-runtime-template>
    </div>
    <div v-else-if="type === 'htmlElement'" ref="htmlElementContainer">
    </div>
    <div v-else>
        {{ data }}
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";
import VRuntimeTemplate from "vue3-runtime-template";


@Component({components: {VRuntimeTemplate}})
class RuntimeComponent extends Vue {
    @Prop type: string
    @Prop content: string
    @Prop data: any

    $refs: { htmlElementContainer: HTMLDivElement }

    updated() {
        if (this.type === 'htmlElement') {
            if (this.$refs.htmlElementContainer !== undefined) {
                this.$refs.htmlElementContainer.append(this.content);
            }
        }
    }
}

export default toNative(RuntimeComponent);
</script>

<style scoped>

</style>