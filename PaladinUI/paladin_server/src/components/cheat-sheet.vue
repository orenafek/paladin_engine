<template>
    <div class="cheat-sheet-container">
        <va-button round icon="help" @click="btnClick" color="#eb6734"/>
        <div :class="{ 'cs': true, 'collapsed': !active }">
            <va-button round icon="help" @click="btnClick" v-if="active" color="#eb6734"/>
            <div style="display: grid; justify-items: center; background-color: #2b2b2b">
                <h3 class="cheat-sheet-header"> Cheat Sheet </h3>
                <div id="docs-container">
                    <div class="doc-section" v-for="d in docs" v-if="active">
                        <h4 class="doc-section-header"> {{ d.type }} </h4>
                        <div class="doc-section-explanation"> {{d.exp }} </div>
                        <code-editor :source-code="d.doc" lang="python"></code-editor>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import CodeEditor from "./code-editor.vue";

@Component({
    components: {CodeEditor}
})
class CheatSheet extends Vue {

    @Prop docs: Array<{ type: string, doc: string, exp: string }>

    active: boolean = false;

    mounted() {
        console.log('docs = ', this.docs);
    }

    btnClick() {
        this.active = !this.active;
    }
}

export default toNative(CheatSheet);

</script>

<style lang="scss" scoped>
.cs {
    position: fixed;
    z-index: 999;
    top: 0;
    right: 0;
    bottom: 0;
    width: 600px; /* Set your desired width */
    transition: transform 0.3s ease-in-out;
    overflow-y: auto;
}

.cheat-sheet-header {
    color: white;
}

.cs.collapsed {
    transform: translateX(100%);
}

.cheat-sheet-container {
    display: flex;
    justify-content: right;
}

.toggle-button-wrapper {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    right: 0;
}

.doc-section {
    display: grid;
}

.doc-section-header {
    justify-self: center;
}

.doc-section-explanation {
    justify-self: left;
    padding-left: 5px;
}
</style>