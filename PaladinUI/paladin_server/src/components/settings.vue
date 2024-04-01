<template>
    <div class="grid-container">
        <va-switch v-model="customizerOpen" color="#eb6734" size="small" @click="customizerSwitchChange"
                   class="grid-item-toggle"></va-switch>
        <label class="grid-item-label"> Customize </label>
    </div>
    <div>
        <Customizer v-if="customizerOpen" :builtin="builtinDisplayers"></Customizer>
    </div>
</template>

<script lang="ts">
import {Component, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import Customizer from "./customizer.vue";
import {Displayers} from "./displayers";


@Component({
    components: {Customizer}
})
class Settings extends Vue {

    customizerOpen: boolean = false
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

}

export default toNative(Settings);
</script>

<style lang="scss" scoped>

@import "../../static/styles/toggle.scss";

.grid-container {
  display: grid;
  grid-template-areas:
        'toggle label'
        'toggle label'
        'toggle label';
}

.grid-item-toggle {
  grid-area: toggle
}

.grid-item-label {
  grid-area: label
}

</style>