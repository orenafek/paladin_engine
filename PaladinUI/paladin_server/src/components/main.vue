<template>
    <div id="app">
        <div id="header">
            <h1 class="headline">PaLaDiN - Time-travel Debugging with Semantic Queries</h1>
            <div class="helpBtnContainer">
                <va-button round icon="help" @click="helpBtnClick" color="#eb6734" class="helpBtn"/>
            </div>
        </div>
        <div id="main">
            <splitpanes class="default-theme" ref="mainSplit" @resize="storeLayoutPanes">
                <pane :size="layout.panes[0].size">
                    <splitpanes horizontal class="default-theme" :push-other-panes="false">
                        <pane :size="codeEditorPaneSize" class="code-editor-pane">
                            <code-editor :source-code="sourceCode" :original-source-code="originalSourceCode"
                                         :actions="actions"
                                         lang="python" ref="editor"
                                         @code-editor-change="codeEditorChange"
                                         @code-editor-reset="codeEditorReset"

                            ></code-editor>
                        </pane>
                        <pane id="program-output-pane" :size="100 - codeEditorPaneSize">
                            <h3 class="section"> Output </h3>
                            <pre class="output" v-text="programOutput"></pre>
                            <div v-if="thrownException.line_no > 0" style="color: red;">
                                {{
                                    `The Program has stopped on line ${thrownException.line_no} with the message: ${thrownException.msg}, on time: ${thrownException.time}`
                                }}
                            </div>
                        </pane>
                    </splitpanes>
                </pane>
                <pane>
                    <splitpanes horizontal class="default-theme" :push-other-panes="false">
                        <pane id="vuebook-pane" :size="100" style="overflow-y: auto">
                            <cheat-sheet ref="cheatSheet" :docs="docs" :examples="examples"></cheat-sheet>
                            <vuebook ref="vuebook" :lastRunTime="lastRunTime"
                                     @highlight="highlightCodeLine" @highlight-stop="stopHighlightCodeLine"></vuebook>
                        </pane>
                    </splitpanes>
                </pane>
            </splitpanes>
        </div> <!-- #main -->
        <div id="spinner-container">
            <screen-loading-spinner v-if="isRerunning"></screen-loading-spinner>
        </div>
    </div> <!-- #app -->
</template>

<script lang="ts">
import {Pane, Splitpanes} from 'splitpanes';
import {Component, Ref, toNative, Vue} from 'vue-facing-decorator';
import './main.scss';
import Slider from "@vueform/slider";
import "@vueform/slider/themes/default.scss";

import {LocalStore, persistField} from "../infra/store";

import {request, request_debug_info, upload} from "../request";

//@ts-ignore
import Vuebook, {IVuebook} from "./vuebook_app.vue";

//@ts-ignore
import CodeEditor from "./code-editor.vue";

//@ts-ignore
import Settings from "./settings.vue";

//@ts-ignore
import ScreenLoadingSpinner from "./screen-loading-spinner.vue";

//@ts-ignore
import CheatSheet from "./cheat-sheet.vue";

type Exception = {
    line_no: number
    throwing_line_source: string
    msg: string
    time: number
}

@Component({
    components: {Splitpanes, Pane, Vuebook, Slider, Settings, CodeEditor, ScreenLoadingSpinner, CheatSheet}
})
class Main extends Vue {

    layout = {panes: [{size: 30}]}
    lastRunTime: number = 0
    timeRange: Array<number> = [0, 0]
    sourceCode: string = ''
    originalSourceCode: string = ''
    programOutput: string = ''
    thrownException: Exception = {} as Exception
    isRerunning: Boolean = false
    docs: string = ''
    examples: Array<[string, string]> = []
    codeEditorPaneSize: number = 85
    @Ref vuebook: IVuebook
    @Ref editor: CodeEditor
    @Ref cheatSheet: CheatSheet

    readonly actions = [
        {
            // name: 'Reset', icon: 'restart_alt', color: "#eb6734", enabled: false, action:
            //     async (updated, original) => {
            //         console.log('in reset callback. original = ', original, ' updated = ', updated);
            //         await this.updateCode(original);
            //         this.sourceCode = original;
            //         await this.rerun();
            //     }
        },
        {
            name: 'Rerun', icon: 'directions_run', color: "#eb6734", enabled: false,
            action: async (updated, original) => {
                await this.updateCode(updated);
                await this.rerun();
            }
        }
    ]

    async created() {
        await this.fetchInitial();
    }

    mounted() {
        persistField(this.layout, 'panes', new LocalStore('main:layout.panes'));
        this.isRerunning = false;
        this.codeEditorPaneSize = this.editor.height();
        console.log('this = ', this);
    }

    async fetchInitial() {
        this.originalSourceCode = (await request_debug_info('source_code') as Array<string>).join('\n');
        this.sourceCode = this.originalSourceCode;
        this.programOutput = await request_debug_info('run_output') as string;
        this.lastRunTime = parseInt((await request_debug_info('last_run_time')).toString());
        this.thrownException = await request_debug_info('thrown_exception') as Exception;
        this.docs = await request_debug_info('docs') as string;
        this.examples = await request_debug_info('examples') as Array<[string, string]>;
        this.$forceUpdate();
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

    async updateCode(updatedCode: string) {
        console.log('in updateCode: updated_code = ', updatedCode);
        await upload(updatedCode, 'upload/source_code');
    }

    async rerun() {
        this.isRerunning = true;
        await request('rerun');
        await this.fetchInitial();
        this.isRerunning = false;
        /* TODO: Fixme!! */
        await (this.vuebook as IVuebook).clearCellOutputs();
        this.$forceUpdate();
    }

    highlightCodeLine(lineNumber: number) {
        (this.editor as CodeEditor).highlightRow(lineNumber);
    }

    stopHighlightCodeLine(lineNumber: number): void {
        (this.editor as CodeEditor).unHighlightRow(lineNumber);
    }

    helpBtnClick() {
        this.cheatSheet.changeDrawer()
    }

    codeEditorChange() {
        /* Change reset button. */
        this.actions[0].enabled = true;
        this.actions[1].enabled = true;
    }

    codeEditorReset() {
        this.actions[0].enabled = false;
        this.actions[1].enabled = false;
    }

}

export default toNative(Main);
</script>

<style lang="scss">
@import 'splitpanes/dist/splitpanes.css';

* {
    box-sizing: border-box;
}

.code-editor-pane {
    display: flex;
    flex-direction: column;

    > .code-editor-container {
        flex-grow: 1;
        > div {
            height: 100%;
        }
    }
}


#header {
    display: grid;
    grid-template-areas: "headline helpBtn";
    padding-right: 10px;
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

.splitpanes.default-theme .splitpanes__pane {
    background-color: #2b2b2b;
}
</style>
