<template>
    <div class="settings-panel">
        <div class="setting">
            <va-switch v-model="customizerOpen" color="#eb6734" size="small" @click="customizerSwitchChange" />
            <label> Customize </label>
            <Customizer v-if="customizerOpen" :builtin="builtinDisplayers" />

        </div>
        <div class="setting">
            <va-switch v-model="auxFilerOpen" color="#eb6734" size="small" @click="auxFilerSwitchChange" />
            <label> Aux File </label>
            <AuxFiler v-if="auxFilerOpen" />
        </div>

    </div>
</template>

<script lang="ts">
import {Component, toNative, Vue} from "vue-facing-decorator";

// @ts-ignore
import Customizer from "./customizer.vue";
import {Displayers} from "./displayers";

// @ts-ignore
import AuxFiler from "./aux-filer.vue";


@Component({
    components: {Customizer, AuxFiler}
})
class Settings extends Vue {

    customizerOpen: boolean = false
    auxFilerOpen: boolean = false

    builtin = []
    builtinDisplayers = [
        {name: 'Array', icon: 'view_array', active: true, file: 'array.js'},
        {name: 'Graph', icon: 'share', active: false, file: 'graph.js'},
        {name: 'Object', icon: 'data_object', active: false, file: 'object.js'}
    ]

    customizerSwitchChange() {
        if (!this.customizerOpen) {
            Displayers.instance.deactivateAll();
        }
    }

    auxFilerSwitchChange() {
        if (!this.auxFilerOpen) {
            console.log(':)');
        }
    }

}

export default toNative(Settings);
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
      'toggle       label     toggle       label'
      'controller   ....      controller';
  grid-template-rows: repeat(2, 1fr);
  //grid-template-columns: repeat4, 1fr);

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