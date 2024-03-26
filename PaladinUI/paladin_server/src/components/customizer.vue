<template>
    <div class="customizer-grid-container">
        <div class="customizer-grid-item-sidebar">
            <va-sidebar width="180px">
                <va-sidebar-item v-for="(d, i) in builtin" @click="setSelected(i, d.name)" ref="items"
                                 :active="d.name === selected">
                    <va-sidebar-item-content>
                        <va-icon :name="d.icon"/>
                        <va-sidebar-item-title>{{ d.name }}</va-sidebar-item-title>
                        <va-switch color="#eb6734" size="small" v-model="displayerSwitches[i]"
                                   @click="switchStateChange(i, d.name)"/>
                    </va-sidebar-item-content>
                </va-sidebar-item>
                <va-sidebar-item>
                    <va-sidebar-item-content>
                        <va-icon name="add_circle_outline"/>
                        <va-sidebar-item-title>Add</va-sidebar-item-title>
                    </va-sidebar-item-content>
                </va-sidebar-item>
            </va-sidebar>
        </div>
        <div class="customizer-grid-item-editor">
            <Codemirror ref="sourceEditor" class="original-style"
                        :value="loadedCustomizer" :readOnly="isLoadedBuiltin"
                        :options="{mode: 'javascript', theme: 'darcula', scrollbarStyle: 'overlay'}"></Codemirror>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, Ref, toNative, Vue} from "vue-facing-decorator";
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import Toggle from "@vueform/toggle";

/* Codemirror imports */
import "codemirror/mode/javascript/javascript";
import "codemirror/theme/darcula.css";
import "codemirror/addon/scroll/simplescrollbars";
import "codemirror/addon/scroll/simplescrollbars.css";
import Codemirror from "codemirror-editor-vue3";
/* ***************** */
import {Displayer, Displayers} from "./displayers";


@Component({
        components: {Toggle, Codemirror}
    }
)
class Customizer extends Vue {
    @Prop builtin?: Displayer[]

    @Ref items: any[]

    selected: string = ''

    displayerSwitches: boolean[] = []

    loadedCustomizer: string = ''
    isLoadedBuiltin: boolean = true;

    async mounted() {
        await Displayers.instance.loadDisplayers(this.builtin);
        this.loadedCustomizer = Displayers.instance.displayers.value[0].source;
    }

    setSelected(ci: number, ck: string) {
        this.selected = ck;
        this.loadedCustomizer = Displayers.instance.displayers.value[ci]?.source;
    }

    switchStateChange(i: number, ck: string) {
        if (this.displayerSwitches[i]) {
            Displayers.instance.activate(ck);
        } else {
            Displayers.instance.deactivate(ck);
        }
    }


}

export default toNative(Customizer);
</script>

<style lang="scss" scoped>
@import "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,400;1,700&display=swap";
@import "https://fonts.googleapis.com/icon?family=Material+Icons";
@import "../../static/styles/toggle.scss";


.customizer-grid-container {
  display: grid;
  grid-template-areas:
        'sidebar editor'
}

.customizer-grid-item-sidebar {
  grid-area: sidebar
}

.customizer-grid-item-editor {
  grid-area: editor
}

</style>