<template>
    <div>
        <command-palette ref="cmd" :commands="commands" @command="onCommand"/>
        <notebook ref="notebook" :model="model" @cell:action="onCellAction"/>
    </div>
</template>

<script lang="ts">
import {h, reactive, watch} from 'vue';
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator';
import {useMagicKeys} from '@vueuse/core';


import {
    CommandPalette,
    Completion,
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
import EmptyResults from "./empty_results.vue";

//@ts-ignore
import {builtinVisualizers} from "./settings.vue";

import {Visualizers} from "./visualizers"

@Component({
    components: {Notebook, CommandPalette, tabular},
    emits: ['highlight', 'highlight-stop']
})
class Vuebook extends Vue {

    @Prop lastRunTime: number
    @Prop completions: Completion[]

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
        this.$watch(() => this.completions, () => {
            this.model.updateCompletions(this.completions);
        });
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

    async clearCellOutputs() {
        for (const cell of this.model.cells) {
            await this.model.clearOutputs(cell);
        }
    }

    private async runCell(cell: Model.Cell) {
        if (cell.input === '') {
            return;
        }

        cell.loading = true;
        let queryRunResult = await request_debug_info("query", ...[cell.input, 0, this.lastRunTime]) as string;
        this.model.clearOutputs(cell);
        const queryError: boolean = this.isError(queryRunResult);
        const emptyResults: boolean = !queryError && this.isResultsEmpty(queryRunResult);
        this.model.addResult(cell,
            queryError ? {
                'application/vue3': {
                    is: h(QueryError),
                    props: {"error": JSON.parse(queryRunResult)['error']}
                }
            } : (emptyResults ? {
                    'application/vue3': {
                        is: h(EmptyResults)
                    }
                } :
                {
                    'application/vue3': {
                        is: h(tabular),
                        props: {
                            "visualizers": builtinVisualizers,
                            "value": this.formatResults(queryRunResult),
                            "emit-event": this.emitEvent
                        }
                    }
                }));

        cell.loading = false;
    }

    private isError(result: string): boolean {
        return JSON.parse(result)['error'] != undefined
    }

    private isResultsEmpty(result: string): boolean {
        return this.formatResults(result).rowHeaders.length == 0;
    }

    async findCausingLineByTime(time: number): Promise<number> {
        const query = "LineNo(InTime(" + time + "))";
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
        } else if (name.includes("row:select")) {
            const lineNumber = await this.findCausingLineByTime(data as number);
            this.$emit("highlight", lineNumber);
        }

    }

    handleControl(action: string) {
        switch (action) {
            case 'rerun-all-cells':
                this.runAllCells();
                break;
            case 'expand-all':
                this.$refs.notebook.expandAll();
                break;
            case 'collapse-all':
                this.$refs.notebook.collapseAll();
                break;
            default:
                this.$refs.notebook.command({command: action});
        }
    }

    focusedCell() {
        return this.$refs.notebook.focusedCell;
    }
}


export {Vuebook as IVuebook, Completion};
export default toNative(Vuebook);
</script>
