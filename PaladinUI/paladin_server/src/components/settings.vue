<template>
    <div class="settings-panel">
        <div class="setting">
            <va-switch v-model="auxFilerOpen" color="#eb6734" size="small" @click="auxFilerSwitchChange"/>
            <label> Aux File </label>
            <AuxFiler v-if="auxFilerOpen"/>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, toNative, Vue} from "vue-facing-decorator";

// @ts-ignore
import {Visualizer, Visualizers} from "./visualizers";

// @ts-ignore
import AuxFiler from "./aux-filer.vue";

const builtinVisualizers: Visualizer[] = [
    {name: 'Array', icon: 'view_array', file: 'array.js'},
    {name: 'Graph', icon: 'share', file: 'graph.js'},
    {name: 'Object', icon: 'data_object', file: 'object.js'},
    {name: 'UnionFind', icon: 'forest', file: 'union_find.js'},
    {name: 'Matrix', icon: 'grid_on', file: 'matrix.js'}
]

@Component({
    components: {AuxFiler}
})
class Settings extends Vue {

    auxFilerOpen: boolean = false

    mounted() {
        Visualizers.instance.loadBuiltinVisualizers(builtinVisualizers);
    }

    auxFilerSwitchChange() {

    }

}

export default toNative(Settings);
export {builtinVisualizers};
</script>

<style lang="scss" scoped>

@import "../../static/styles/toggle.scss";

.settings-panel {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.setting {
  display: grid;
  grid-template-columns: auto auto;
  grid-template-rows: auto;
  gap: 5px;
  align-items: center;
}

.grid-container {
  display: grid;
  grid-template-areas:
      'toggle       label'
      'controller';
  grid-template-rows: repeat(2, 1fr);
}

.grid-item-toggle {
  grid-area: toggle
}

.grid-item-label {
  grid-area: label
}

.grid-item-controller {
  grid-area: controller;
}

</style>