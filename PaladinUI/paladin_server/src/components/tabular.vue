<template>
    <table v-if="value?.columnHeaders">
        <thead>
        <td>Time</td>
        <td v-for="h in value.columnHeaders"> {{ h }}</td>
        </thead>
        <tr v-for="rowHead in value.rowHeaders">
            <td @click="rowSelect($event, rowHead)"> {{ rowHead.display }}</td>
            <td v-for="colKey in value.columnHeaders">
                <runtime-component :column="colKey" v-bind="result(rowHead.key, colKey)"></runtime-component>
            </td>
        </tr>
    </table>
</template>

<script lang="ts">
import {Ref} from 'vue';
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";
import {Displayer, Displayers} from "./displayers";

//@ts-ignore
import RuntimeComponent from "./runtime-component.vue";

@Component({
    components: {RuntimeComponent},
    emits: ['row:select']
})
class Tabular extends Vue {
    @Prop value: any

    result(rowKey: string, colKey: string) {
        let displayers: Ref<Displayer[]> = Displayers.instance.active;
        let item = this.value.rowData[rowKey]?.[colKey];

        for (const displayer of displayers.value) {
            try {
                if (displayer.instance.matches(item)) {
                    return {...displayer.instance.format(item), data: item};
                }
            } catch (error) {
                console.log("Error: " + error);
                this.$emit('customizedCodeError', error.toString());
            }
        }

        return {type: "text/plain", content: item, data: item};
    }

    rowSelect($event, rowHead) {
        this.$emit('row:select', {$event, rowHead});
    }
}

export default toNative(Tabular);
</script>

<style scoped>
table, th, thead, td {
    border: 1px solid;
}
</style>