<template>
    <table v-if="value?.columnHeaders">
        <thead class="fixedHeader">
        <tr>
            <th>Time</th>
            <th v-for="h in value.columnHeaders">
                <div>{{ h }}</div>
                <div>
                    <visualizer-panel ref="visPanel" :visualizers="availableVisualizers(h)" :column="h"
                                      @active-change="activeVisChanged"/>
                </div>

            </th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="rowHead in value.rowHeaders">
            <td @click="rowSelect($event, rowHead)" class="hover-underline"> {{ rowHead.display }}</td>
            <td v-for="colKey in value.columnHeaders">
                <div style="display: inline-flex;">
                    <runtime-component ref="rc" :column="colKey" v-bind="results[rowHead.key][colKey]" />
                    <span :style="'color: '+ results[rowHead.key][colKey].color + '; font-size: 8pt'">*</span>
                </div>
            </td>
        </tr>
        </tbody>
    </table>
</template>

<script lang="ts">

import {Component, Prop, toNative, Vue} from "vue-facing-decorator";
import {Visualizer, Visualizers} from "./visualizers";
import {toEntries} from "../infra/common"
//@ts-ignore
import RuntimeComponent from "./runtime-component.vue";

//@ts-ignore
import VisualizerPanel from "./visualizer-panel.vue";

interface TabularValue {
    columnHeaders: string[]
    rowHeaders: { key: string, display: string }[]
    rowData: string[][]
}

type CellData = {
    type: string
    content: any
    data: any
    color: string
}


@Component({
    components: {RuntimeComponent, VisualizerPanel},
    emits: ['row:select']
})
class Tabular extends Vue {
    COLOR_CLEAR = 'rgba(0, 0, 0, 0)';
    COLOR_CHANGE = '#ffc66d';

    @Prop value: TabularValue
    @Prop emitEvent: any

    results: { [row: string]: { [col: string]: CellData } } = {};

    $refs: { visPanel: VisualizerPanel[], rc: RuntimeComponent[] }

    created() {
        this.initializeResults();
    }

    activeVisChanged(column: string, active: Visualizer[]) {
        this.value.rowHeaders.map(rh => rh.key).forEach((row, rowIndex) => {
            this.updateResult(row, column, active);
        })
    }

    updateResult(row: string, col: string, visualizers: Visualizer[]) {
        if (!this.results[row]) {
            this.results[row] = {}
        }

        let item = this.value.rowData[row]?.[col];
        if (visualizers.length == 0) {
            this.results[row][col] = this.plainResult(row, col);
            return;
        }

        try {
            let visualized = false;
            for (const visualizer of visualizers.values()) {
                if (visualizer.instance.matches(item)) {
                    this.results[row][col] = {
                        ...visualizer.instance.format(item),
                        data: item != null ? item : '',
                        color: this.COLOR_CLEAR
                    };
                    visualized = true;
                    /* For now, select the first active, available visualizer to prevent conflicts. */
                    break;
                }
            }
            if (!visualized) {
                this.results[row][col] = this.plainResult(row, col);
            }

        } catch (error) {
            console.log('error : ', error);
            this.$emit('VisualizerError', error.toString());
        }
    }


    private plainResult(row: string, col: string): any {
        const item = this.value.rowData[row]?.[col];
        return ({type: "text/plain", content: item, data: item != null ? item : '', color: this.COLOR_CLEAR});
    }

    initializeResults() {
        let lastRow = [];
        for (const [row_index, row] of toEntries(this.value.rowHeaders)) {
            this.results[row.key] = {}
            for (const [col_index, col] of toEntries(this.value.columnHeaders)) {
                let cell = this.results[row.key][col] = this.plainResult(row.key, col);
                if (row_index != 0) {
                    if (lastRow[col_index] !== cell.data) {
                        cell.color = this.COLOR_CHANGE;
                    }
                }
                lastRow[col_index] = cell.data;
            }
        }
    }

     rowSelect($event, rowHead) {
        const regex = /\((\d+),\s*\d+\)/;
        const match = regex.exec(rowHead.key);

        // Execute the regular expression on the string
        if (!match) {
            console.error('Tabular row key is not in an appropriate format.');
        }

        const leftTime = parseInt(match[1]);
        this.emitEvent('row:select', leftTime);
    }

    availableVisualizers(column: string): Visualizer[] {
        return [...new Set(this.value.rowHeaders.flatMap(
            row => Visualizers.instance.matches(this.value.rowData[row.key]?.[column])))];
    }

}

export default toNative(Tabular);
</script>

<style scoped>
table, th, thead, td {
    border: 1px solid;
}

th {
    top: 0;
    position: sticky;
    z-index: 5;
    justify-content: left;
}

td.hover-underline:hover {
    text-decoration: underline;
}

</style>