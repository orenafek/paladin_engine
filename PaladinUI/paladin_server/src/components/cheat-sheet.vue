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
.cheat-sheet-container {
    display: flex;
    justify-content: right;
}
</style>