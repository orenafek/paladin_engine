<template>
    <div>
        <command-palette ref="cmd" :commands="commands" @command="onCommand"/>
        <notebook ref="notebook" :model="model" @cell:action="onCellAction" :codeEditorType="codeEditorType" :completions="completions"/>
    </div>
</template>

<script lang="ts">
import {h, reactive, watch} from 'vue';
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator';
import {useMagicKeys} from '@vueuse/core';


import {
    CodeEditor,
    CommandPalette,
    Completion,
    EditorView,
    ICodeEditor,
    ICommandPalette,
    INotebook,
    Model,
    ModelImpl,
    Notebook,
    NotebookActions
} from 'vuebook';

import {request_debug_info} from "../request";

//@ts-ignore
import tabular from "./tabular.vue";


@Component({
    components: {Notebook, CommandPalette, tabular}
})
class Vuebook extends Vue {

    readonly codeEditorType: ICodeEditor = PaladinCompletions

    @Prop completions: Completion[]
    @Prop lastRunTime: number

    model: ModelImpl
    control: NotebookActions

    commands = ["exec", "exec-fwd", "insert-after", "go-down", "delete", "clear"]

    $refs: { cmd: ICommandPalette, notebook: INotebook }

    created() {
        this.model = reactive(new ModelImpl()).load();
        this.model.clearAllOutputs();
        window.addEventListener('beforeunload', () => this.model.save());

        const keys = useMagicKeys()
        watch(keys['Meta+K'], (v) => v && this.$refs.cmd.open());
        watch(keys['Escape'], (v) => v && this.$refs.cmd.close());
        watch(keys['Down'], (v) => v && this.$refs.cmd.close());
    }

    mounted() {
        console.log('vuebook_app.vue: this.completions = ', this.completions);
        console.log('vuebook_app.vue: this.completions.length = ', this.completions.length);
        this.$watch(() => this.completions, v => {
            console.log('vuebook_app.vue: $watch(this.completions), v = ', v);
        });
    }

    onCommand(command: { command: string }) {
        console.log('vuebook_app.vue:: onCommand: this.completions = ', this.completions);
        this.$refs.notebook.command(command);
    }

    formatResults(queryResult) {
        return {
            columnHeaders: queryResult['keys'],
            rowHeaders: Object.keys(queryResult).filter(k => k != 'keys')
                .map(key => ({key, display: this.formatTimeInterval(key)})),
            rowData: queryResult
        };
    }

    formatTimeInterval(s) {
        const regex = /\((\d+), (\d+)\)/;
        const matched = s.match(regex);
        if (matched[1] === matched[2]) {
            return matched[1].toString();
        }

        return s.replace(regex, '$1–$2');
    }

    async onCellAction(action: { cell?: Model.Cell, type: string }) {
        switch (action.type) {
            case 'exec':
            case 'exec-fwd': {
                await this.runCell(action.cell);
            }
        }
    }

    async runAllCells() {
        for (const cell of this.model.cells) {
            await this.runCell(cell);
        }
    }

    private async runCell(cell: Model.Cell) {
        cell.loading = true;
        let queryRunResult = await request_debug_info("query", ...[cell.input, 0, this.lastRunTime, ""]);
        this.model.clearOutputs(cell);
        this.model.addResult(cell,
            {
                'application/vue3': {
                    is: h(tabular),
                    props: {"value": this.formatResults(JSON.parse(queryRunResult as string))}
                }
            });

        cell.loading = false;
    }
}

class PaladinCompletions extends CodeEditor {

    private _completions: Completion[]

    constructor(container: HTMLElement, initialContent?: string, completions: Completion[] = []) {
        super(container, initialContent);
        this._completions = completions.map((c) => {
            return {...c, apply: this.applyCompletion}
        });
        console.log('PaladinCompletions: completions = ', completions);
    }

    get completions(): Completion[] {
        console.log('vuebook_app.vue:: PaladinCompletions::completions(), this._completions = ', this._completions);
        return this._completions;
    }

    applyCompletion(ev: EditorView, c: Completion, from: number, to: number) {
        console.log('vuebook_app.vue: applyCompletion, c = ', c);
        const newText = c.label + '()';
        ev.dispatch(ev.state.update({
            changes: {
                from: from,
                to: to,
                insert: newText,
            },
            selection: {
                anchor: from + newText.length - 1,
                head: from + newText.length - 1
            }
        }));
    }
}

export {Vuebook as IVuebook, Completion};
export default toNative(Vuebook);
</script>