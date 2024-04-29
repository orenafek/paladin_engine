<template>
    <div class="header-container">
        <h1>PaLaDiN Cheat Sheet</h1>
    </div>
    <div class="doc-section" v-for="d in docs">
        <h4 class="doc-section-header"> {{ d.type }} </h4>
        <div class="doc-section-explanation"> {{ d.exp }}</div>
        <code-editor :source-code="d.doc" lang="python"></code-editor>
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import CodeEditor from "./code-editor.vue";

type Doc = {
    type: string
    doc: string
    exp: string
};

@Component({components: {CodeEditor}})
class PaladinDoc extends Vue {
    @Prop docs: Array<Doc>
}

export default toNative(PaladinDoc);

</script>

<style lang="scss" scoped>

.header-container {
    display: grid;
    justify-content: center;
}

.doc-section {
    display: grid;
}

.doc-section-header {
}

.doc-section-explanation {
    justify-self: left;
    padding-left: 5px;
}
</style>