<template>
    <div id="header">
        <h1 class="headline">PaLaDiN - Time-travel Debugging with Semantic Queries</h1>
        <div id="controls">
            <control-panel class="cntrl-panel" :focused-cell="focusedCell" @control="emitControl" />
<!--            <div class="helpBtnContainer">-->
<!--                <va-button round icon="help" @click="$emit('help-btn-click')" color="#eb6734" class="helpBtn"/>-->
<!--            </div>-->
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import ControlPanel from "./control-panel.vue";

@Component({
    components: {ControlPanel},
    emits: ['help-btn-click', 'control']
})
class PaladinHeader extends Vue {

    @Prop focusedCell: boolean

    private emitControl(action: string){
        this.$emit('control', action);
    }
}

export default toNative(PaladinHeader);

</script>

<style lang="scss" scoped>

#header {
    display: grid;
    grid-template-areas: "headline controls";
    padding-right: 10px;
    align-items: center;
}

.headline {
    grid-area: headline;
}

.helpBtnContainer {
    padding-top: 2px;
    justify-self: right;
}

.helpBtn {
    grid-area: helpBtn;
    max-width: 40px;
    justify-self: right;
}

#controls {
    grid-area: controls;
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
}

</style>