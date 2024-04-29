<template>
    <div class="cheat-sheet-container">
        <drawer :content="paladinDoc"
                :content-props="{docs: docs}"
                :is-open="drawerOpen" :max-width="maxWidth"
                @close="drawerOpen = false">
        </drawer>
    </div>

</template>

<script lang="ts">
import {h} from "vue";
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import Drawer from "./drawer.vue";

//@ts-ignore
import PaladinDoc from "./paladin-doc.vue";

@Component({
    components: {Drawer, PaladinDoc}
})
class CheatSheet extends Vue {

    @Prop docs: Array<{ type: string, doc: string, exp: string }>

    readonly maxWidth: string = '750px';

    drawerOpen: boolean = false;
    paladinDoc: typeof PaladinDoc = null;


    mounted() {
        this.paladinDoc = h(PaladinDoc);
    }

    changeDrawer() {
        this.drawerOpen = !this.drawerOpen;
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