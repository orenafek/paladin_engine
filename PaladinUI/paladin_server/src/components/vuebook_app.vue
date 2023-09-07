<template>
    <div>
        <command-palette ref="cmd" :commands="commands" @command="onCommand"/>
        <notebook ref="notebook" :model="model" @cell:action="onCellAction"/>
    </div>
</template>

<script lang="ts">
import {h, reactive, watch} from 'vue';
import {Component, toNative, Vue} from 'vue-facing-decorator';
import {useMagicKeys} from '@vueuse/core';


import {CommandPalette, ICommandPalette, INotebook, Model, ModelImpl, Notebook, NotebookActions} from 'vuebook';

import {request_debug_info} from "../request";

//@ts-ignore
import tabular from "./tabular.vue";


@Component({
    components: {Notebook, CommandPalette, tabular}
})
class Vuebook extends Vue {
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
        watch(keys['Down'], (v) => v && this.$refs.cmd.close())
    }

    onCommand(command: { command: string }) {
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
        return s.replace(/\((\d+), (\d+)\)/, '$1–$2');
    }

    async onCellAction(action: { cell?: Model.Cell, type: string }) {
        switch (action.type) {
            case 'exec':
            case 'exec-fwd': {
                let queryRunResult = await request_debug_info("query", ...[action.cell.input, 0, 500, ""]);
                this.model.addResult(action.cell,
                    {
                        'application/vue3': {
                            is: h(tabular),
                            props: {"value": this.formatResults(JSON.parse(queryRunResult as string))}
                        }
                    });
            }
        }
    }
}

export default toNative(Vuebook);
</script>