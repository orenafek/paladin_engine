<template>
    <div>
        <command-palette ref="cmd" :commands="commands" @command="onCommand"/>
        <notebook ref="notebook" :model="model" @cell:action="onCellAction" />
    </div>
</template>

<script lang="ts">
import {h, reactive, watch} from 'vue';
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator';
import {useMagicKeys} from '@vueuse/core';


import {
    CommandPalette,
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

//@ts-ignore
import QueryError from "./query_error.vue"

//@ts-ignore
import {builtinVisualizers} from "./settings.vue";

import {Visualizers} from "./visualizers"

@Component({
    components: {Notebook, CommandPalette, tabular},
    emits: ['highlight', 'highlight-stop']
})
class Vuebook extends Vue {

    @Prop lastRunTime: number

    model: ModelImpl
    control: NotebookActions

    commands = ["exec", "exec-fwd", "insert-after", "go-down", "delete", "clear"]

    $refs: { cmd: ICommandPalette, notebook: INotebook }

    created() {
        this.model = reactive(new ModelImpl()).load();
        this.model.clearAllOutputs();
        this.model.resetLoading();
        window.addEventListener('beforeunload', () => this.model.save());

        const keys = useMagicKeys()
        watch(keys['Meta+K'], (v) => v && this.$refs.cmd.open());
        watch(keys['Escape'], (v) => v && this.$refs.cmd.close());
        watch(keys['Down'], (v) => v && this.$refs.cmd.close());
    }

    async mounted() {
        await Visualizers.instance.loadBuiltinVisualizers(builtinVisualizers);
    }

    onCommand(command: { command: string }) {
        this.$refs.notebook.command(command);
    }

    formatResults(queryResult) {
        let qr = JSON.parse(queryResult as string);
        return {
            columnHeaders: qr['keys'],
            rowHeaders: Object.keys(qr).filter(k => k != 'keys')
                .map(key => ({key, display: this.formatTimeInterval(key)})),
            rowData: qr
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
        let queryRunResult = await request_debug_info("query", ...[cell.input, 0, this.lastRunTime, ""]) as string;
        this.model.clearOutputs(cell);
        this.model.addResult(cell,
            !this.isError(queryRunResult) ?
                {
                    'application/vue3': {
                        is: h(tabular),
                        props: {
                            "visualizers": builtinVisualizers,
                            "value": this.formatResults(queryRunResult),
                            "emit-event": this.emitEvent
                        }
                    }
                } :
                {
                    'application/vue3': {
                        is: h(QueryError),
                        props: {"error": JSON.parse(queryRunResult)['error']}
                    }
                });

        cell.loading = false;
    }

    private isError(result: string): boolean {
        return JSON.parse(result)['error'] != undefined
    }

    async findCausingLineByTime(time: number): Promise<number> {
        const query = "LineNo(ConstTime(" + time + "))";
        const queryRunResult = await request_debug_info("query", ...[query, time, time]);
        const results = this.formatResults(queryRunResult);
        try {
            return parseInt(results.rowData[results.rowHeaders[0].key][results.columnHeaders[0]]);
        } catch (error) {
            console.error("vuebook_app: wrong lineNumber.");
        }

        return -1;
    }


    async emitEvent(name: string, data: any) {
        if (name.includes("row:unselect")) {
            const lineNumber = await this.findCausingLineByTime(data as number);
            this.$emit("highlight-stop", lineNumber);
        }

        else if (name.includes("row:select")) {
            const lineNumber = await this.findCausingLineByTime(data as number);
            this.$emit("highlight", lineNumber);
        }

    }
}

// class PaladinCompletions extends CodeEditor {
//
//     private _completions: Completion[]
//
//     constructor(container: HTMLElement, initialContent?: string, completions: Completion[] = []) {
//         super(container, initialContent);
//         this._completions = completions.map((c) => {
//             return {...c, apply: this.applyCompletion}
//         });
//     }
//
//     get completions(): Completion[] {
//         return this._completions;
//     }
//
//     applyCompletion(ev: EditorView, c: Completion, from: number, to: number) {
//         const newText = c.label + '()';
//         ev.dispatch(ev.state.update({
//             changes: {
//                 from: from,
//                 to: to,
//                 insert: newText,
//             },
//             selection: {
//                 anchor: from + newText.length - 1,
//                 head: from + newText.length - 1
//             }
//         }));
//     }
// }

export {Vuebook as IVuebook};
export default toNative(Vuebook);
</script>
