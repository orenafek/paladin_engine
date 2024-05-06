<template>
    <div>
        <table>
            <tr>
                <td v-for="v in visualizers">
                    <va-button preset="secondary" color="#eb6734" hover-behavior="opacity"
                              :icon="v.icon" :hover-opacity="0.4" size="small" @click="buttonClick(v)" :disabled="shouldDisable(v)" />
                </td>
            </tr>
        </table>
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";
import {Visualizer} from "./visualizers";

@Component({
    emits: ['active-change']
})
class VisualizerPanel extends Vue {
    @Prop column: string
    @Prop visualizers?: Visualizer[]

    _active: Visualizer[] = []
    btnState: boolean[];


    created() {
        this.btnState = new Array<boolean>(this.visualizers.length);

    }

    mounted() {
        this.btnState = new Array<boolean>(this.visualizers.length);
    }

    buttonClick(v) {
        if (this._active[this.indexOf(this._active, v)]) {
            this.deactivate(v);
        } else {
            this.activate(v);
        }

        this.$emit('active-change', this.column, this._active);
        this.btnState[this.indexOf(this.visualizers, v)] = !this.btnState[this.indexOf(this.visualizers, v)];
    }

    activate(v: Visualizer) {
        this._active.push(v);
    }

    deactivate(v: Visualizer) {
        this._active.splice(this.indexOf(this._active, v), 1);
    }

    private indexOf(c: Visualizer[], v: Visualizer): number {
        for (let i = 0; i < c.length; i++) {
            if (c[i].name === v.name) {
                return i;
            }
        }
        return -1;
    }

    shouldDisable(v: Visualizer): boolean {
        return this._active.length > 0 && this.indexOf(this._active, v) == -1;
    }

    active(): Visualizer[] {
        return this._active;
    }
}

export default toNative(VisualizerPanel);

</script>

<style lang="scss" scoped>
@import "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,400;1,700&display=swap";
@import "https://fonts.googleapis.com/icon?family=Material+Icons";

table tr th td {
  border-width: 0;
}
</style>