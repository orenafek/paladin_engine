<template>
<<<<<<< Updated upstream
    <div v-if="type === 'text/html'">
        <v-runtime-template :template="content"></v-runtime-template>
    </div>
    <div v-else-if="type === 'htmlElement'" ref="htmlElementContainer">
    </div>
    <div v-else>
        {{ data }}
=======
    <div @contextmenu="onContextMenu($event)">
<!--        <cell-menu :whyQuestion="`${column} = ${content}`" :show="show" :pos="pos"/>-->
        <div v-if="type === 'text/html'">
            <v-runtime-template :template="content"></v-runtime-template>
        </div>
        <div v-else>
            {{ data }}
        </div>
>>>>>>> Stashed changes
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";
import VRuntimeTemplate from "vue3-runtime-template";

// @ts-ignore
import CellMenu, {IPos} from "./cell-menu.vue";

@Component({components: {VRuntimeTemplate, CellMenu}})
class RuntimeComponent extends Vue {
    @Prop type: string
    @Prop content: string
    @Prop data: any
<<<<<<< Updated upstream

    $refs: { htmlElementContainer: HTMLDivElement }

    updated() {
        if (this.type === 'htmlElement') {
            if (this.$refs.htmlElementContainer !== undefined) {
                this.$refs.htmlElementContainer.append(this.content);
            }
        }
=======
    @Prop column: string

    show: boolean = false
    pos: IPos = {x: 0, y: 0}

    onContextMenu(e: MouseEvent) {
        console.log('RuntimeComponent, onContextMenu, e = ', e);
        e.preventDefault();
        this.pos = {x: e.x, y: e.y};
        this.show = true;

>>>>>>> Stashed changes
    }
}

export default toNative(RuntimeComponent);
</script>

<style scoped>

</style>