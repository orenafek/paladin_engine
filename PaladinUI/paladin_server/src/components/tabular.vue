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
            <td @click="rowSelect($event, rowHead)"> {{ rowHead.display }}</td>
            <td v-for="colKey in value.columnHeaders">
                <runtime-component ref="rc" :column="colKey" v-bind="results[rowHead.key][colKey]">
                </runtime-component>
            </td>
        </tr>
        </tbody>
    </table>
</template>

<script lang="ts">

import {Component, Prop, toNative, Vue} from "vue-facing-decorator";
import {Visualizer, Visualizers} from "./visualizers";

//@ts-ignore
import RuntimeComponent from "./runtime-component.vue";

//@ts-ignore
import VisualizerPanel from "./visualizer-panel.vue";

interface TabularValue {
    columnHeaders: string[]
    rowHeaders: { key: string, display: string }[]
    rowData: string[][]
}

@Component({
    components: {RuntimeComponent, VisualizerPanel},
    emits: ['row:select']
})
class Tabular extends Vue {
    @Prop value: TabularValue

    results: { [row: string]: { [col: string]: any } } = {};

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
                    this.results[row][col] = {...visualizer.instance.format(item), data: item != null ? item : ''};
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
        return ({type: "text/plain", content: item, data: item != null ? item : ''});
    }

    initializeResults() {
        for (const row of this.value.rowHeaders) {
            this.results[row.key] = {};
            for (const col of this.value.columnHeaders) {
                this.results[row.key][col] = this.plainResult(row.key, col);
            }
        }
    }

    rowSelect($event, rowHead) {
        this.$emit('row:select', {$event, rowHead});
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

</style>