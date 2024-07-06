<template>
    <div class="control-panel">
        <button
            v-for="(action, name) in actions"
            :key="name"
            :title="action.label"
            @click="emitAction(name)"
            :disabled="shouldDisable(action.disabledOnNoneFocused)"
        >
            <i :class="action.icon" :style="{ color: action.color }" />
            <div> &nbsp; </div>
            <div v-if="action.displayText" class="text-btn"> {{ action.label }}</div>
        </button>
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

@Component({
    emits: ['control']
})
class ControlPanel extends Vue {
    @Prop focusedCell: boolean

    actions = {
        exec: {label: 'Run Cell', icon: 'fas fa-play', disabledOnNoneFocused: true, color: 'white', displayText: false},
        insertAfter: {label: 'Add Cell', icon: 'fas fa-plus', disabledOnNoneFocused: true, color: 'white', displayText: false},
        delete: {label: 'Delete Cell', icon: 'fas fa-minus', disabledOnNoneFocused: true, color: 'white', displayText: false},
        goUp: {label: 'Move Up', icon: 'fas fa-arrow-up', disabledOnNoneFocused: true, color: 'white', displayText: false},
        goDown: {label: 'Move Down', icon: 'fas fa-arrow-down', disabledOnNoneFocused: true, color: 'white', displayText: false},
        ExpandAll: {label: 'Expand All', icon: 'fas fa-expand', disabledOnNoneFocused: false, color: 'white', displayText: false},
        collapseAll: {label: 'Collapse All', icon: 'fas fa-compress', disabledOnNoneFocused: false, color: 'white', displayText: false},
        rerunAllCells: {label: 'Rerun All Cells', icon: 'fas fa-forward', disabledOnNoneFocused: false, color: 'white', displayText: false},
        runProg: {label: 'Run Program', icon: 'fas fa-person-running', disabledOnNoneFocused: false, color: '#eb6734', displayText: true},
        help: {label: 'Cheat Sheet', icon: 'fas fa-question', disabledOnNoneFocused: false, color: '#eb6734', displayText: true}
    };

    private emitAction(name: string) {
        this.$emit('control', this.camel2Kebab(name));
    }

    private camel2Kebab(s: string): string {
        return s.replace(/([a-z0-9])([A-Z])/g, '$1-$2').replace(/([A-Z])([A-Z][a-z])/g, '$1-$2').toLowerCase();
    }

    private shouldDisable(disableOnNoneFocused: boolean): boolean {
        return disableOnNoneFocused && !this.focusedCell;
    }

}

export default toNative(ControlPanel);
</script>

<style lang="scss" scoped>
@import '@fortawesome/fontawesome-free/css/all.css';

.control-panel {
    display: flex;
    gap: 10px;
    background-color: #444444;
    padding: 10px;
    justify-content: center; /* Center the buttons horizontally */
    flex-wrap: wrap; /* Allow wrapping to fit container */
}

button {
    background-color: #3c3c3c;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 8px; /* Increased padding */
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s, border-color 0.2s;
}

button i {
    font-size: 16px; /* Increased font size */
    color: white;
}

button:hover {
    background-color: #4c4c4c;
    border-color: #555;
}

button:active {
    background-color: #5c5c5c;
    border-color: #666;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

.text-btn {
    color: #eb6734
}

</style>
