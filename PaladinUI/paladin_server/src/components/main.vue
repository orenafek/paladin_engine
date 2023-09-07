<template>
    <div id="app">
        <div id="header">
            <h1 style="position: center">PaLaDiN - Time-travel Debugging with Semantic Queries</h1>
        </div>
        <div id="main">
            <splitpanes class="default-theme" ref="mainSplit" @resize="storeLayoutPanes">
                <pane :size="layout.panes[0].size">
                    <Codemirror id="source-editor" ref="sourceEditor" class="original-style"
                                :value="sourceCode.join('\n')"
                                :options="{mode: 'python', theme: 'darcula', scrollbarStyle: 'overlay'}"></Codemirror>
                </pane>
                <pane>
                    <splitpanes horizontal class="default-theme" :push-other-panes="false">
                        <pane id="settings-pane" size="15">
                            <div class="range-spec">
<!--                                <Slider id="queryTimeSlider" :min="0" :max="lastRunTime" :value="timeRange"-->
<!--                                        @change="sliderChange"></Slider>-->
<!--                                <label>Time range</label>-->
                            </div>
                        </pane>
                        <pane id="vuebook-pane">
                            <vuebook></vuebook>
                        </pane>
                    </splitpanes>
                </pane>
            </splitpanes>
        </div> <!-- #main -->
    </div> <!-- #app -->
</template>

<script lang="ts">
import {Pane, Splitpanes} from 'splitpanes';
import {Component, toNative, Vue} from 'vue-facing-decorator';
import './main.scss';
import 'splitpanes/dist/splitpanes.css';
import Slider from "@vueform/slider";
import "@vueform/slider/themes/default.scss";
//@ts-ignore
import Vuebook from "./vuebook_app.vue";
// //@ts-ignore
// import Tabular from "./tabular.vue";

import {LocalStore, persistField} from "../infra/store";
/* Codemirror imports */
import "codemirror/mode/python/python.js";
import "codemirror/theme/darcula.css";
import "codemirror/addon/scroll/simplescrollbars";
import "codemirror/addon/scroll/simplescrollbars.css";
import Codemirror from "codemirror-editor-vue3";

import {request_debug_info} from "../request";


@Component({
    components: {Splitpanes, Pane, Vuebook, Codemirror, Slider}
})
class Main extends Vue {

    layout = {panes: [{size: 30}]}
    lastRunTime: number = 0;
    timeRange: Array<number> = [0, 0];
    sourceCode: Array<string> = [];

    async created() {
        await this.fetchInitial();
    }

    mounted() {
        persistField(this.layout, 'panes', new LocalStore('main:layout.panes'));
    }

    async fetchInitial() {
        this.sourceCode = await request_debug_info('source_code') as Array<string>;
        this.lastRunTime = parseInt((await request_debug_info('last_run_time')).toString());
        this.resetSlider();
    }

    storeLayoutPanes(ev) {
        this.layout.panes = ev.map(x => ({size: x.size}));
    }

    sliderChange(sliderValue) {
        this.timeRange[0] = sliderValue[0];
        this.timeRange[1] = sliderValue[1];
    }

    private resetSlider() {
        this.timeRange = [0, this.lastRunTime];
    }
}

export default toNative(Main);
</script>