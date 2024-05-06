<template>
    <div>
        <div class="graph-container">
            <div class="number-line">
                <div class="tick" v-for="tick in archiveLength" :key="tick">{{ tick }}</div>
                <div class="operator" v-for="operator in operators" :key="operator.name">
                    {{ operator.name }}:
                    <span v-for="(result, index) in operatorResults[operator.name]" :key="index"
                          :style="{ left: `${result * 20}px` }">
            {{ result }}
          </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

@Component
class TimeOperatorGraph extends Vue {

    @Prop operator: string
    @Prop archiveLength: number

    operatorResults: Array<any>

    created() {
        this.computeOperatorResults();
    }

    computeOperatorResults() {
        // Logic to compute results of the operator based on archive length and operands
        switch (this.operator) {
            case "After":
                this.computeAfterOperatorResults();
                break;
            case "And":
                this.computeAndOperatorResults();
                break;
            // Add cases for other operators
            default:
                this.setDefaultResults();
                break;
        }
    }

    computeAfterOperatorResults() {
        // Logic for After operator
        const results = [];
        results.push(0); // First event is always satisfied
        for (let i = 1; i < this.archiveLength; i++) {
            if (i >= this.getOperandValue("o")) {
                results.push(1);
            } else {
                results.push(0);
            }
        }
        this.operatorResults = results;
    }

    computeAndOperatorResults() {
        // Logic for And operator
        const operand1Results = this.getOperandResults("o1");
        const operand2Results = this.getOperandResults("o2");
        const results = operand1Results.map((value, index) => value && operand2Results[index] ? 1 : 0);
        this.operatorResults = results;
    }

    getOperandValue(operand) {
        // Logic to get the value of an operand
        // Implement logic based on the operand format specified in your documentation
        // For simplicity, returning 0 as dummy value
        return 0;
    }

    getOperandResults(operand) {
        // Logic to get the results of an operand
        // For simplicity, returning an array of all 0s
        return Array(this.archiveLength).fill(0);
    }

    setDefaultResults() {
        // Default logic if not implemented for a specific operator
        this.operatorResults = Array(this.archiveLength).fill(0);
    }

}

export default toNative(TimeOperatorGraph);

</script>

<style lang="scss" scoped>
.graph-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.number-line {
  display: flex;
  align-items: center;
  margin-top: 20px;
}
.tick {
  width: 20px;
  text-align: center;
}
.operator {
  position: relative;
  margin-top: 10px;
}
.operator span {
  position: absolute;
  bottom: 0;
  transform: translateX(-50%);
}
</style>
