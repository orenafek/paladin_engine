<template>
    <div class="cheat-sheet-container">
        <h1 class="cheat-sheet-title">PaLaDiN Cheat Sheet</h1>

        <section class="cheat-sheet-section">
            <div class="section-header" @click="toggleSection('shortcuts')">
                <span class="collapse-icon" v-html="getCollapseIcon('shortcuts')"></span>
                Keyboard Shortcuts
            </div>
            <div class="shortcuts-container" v-show="sections.shortcuts">
                <div class="shortcuts-column">
                    <ul class="shortcuts-list">
                        <li v-for="(shortcut, index) in columnOneShortcuts" :key="`shortcut-${index}`">
                            <span v-for="(key, i) in shortcut.keys" :key="`key-${i}`" class="keyboard-key">
                                {{ key }}
                            </span>: {{ shortcut.action }}
                        </li>
                    </ul>
                </div>
                <div class="shortcuts-column">
                    <ul class="shortcuts-list">
                        <li v-for="(shortcut, index) in columnTwoShortcuts"
                            :key="`shortcut-${index + columnOneShortcuts.length}`">
                            <span v-for="(key, i) in shortcut.keys" :key="`key-${i}`" class="keyboard-key">
                                {{ key }}
                            </span>: {{ shortcut.action }}
                        </li>
                    </ul>
                </div>
            </div>
        </section>

        <section class="cheat-sheet-section">
            <div class="section-header" @click="toggleSection('operators')">
                <span class="collapse-icon" v-html="getCollapseIcon('operators')"></span>
                Operators
            </div>
            <div class="operators-container" v-show="sections.operators">
                <section class="operators-section">
                    <section v-for="(item, index) in docs" :key="index" class="cheat-sheet-section">
                        <h2 class="section-header">{{ item.type }}</h2>
                        <p class="section-description">{{ item.exp }}</p>
                        <div class="documentation">
                            <!-- Splitting documentation by line and then by operator parts -->
                            <div v-for="(doc, i) in parseDoc(item.doc)" :key="`doc-${i}`" class="operator-block">
                                <span class="operator-name">{{ doc.name }}(</span>
                                <span class="operator-params">{{ doc.params }}</span>
                                <span class="operator-name">):</span>
                                <span class="operator-description" v-html="doc.description"></span>
                            </div>
                        </div>
                    </section>
                </section>
            </div>
        </section>
    </div>
</template>

<script lang="ts">
import {Component, Prop, Ref, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import CodeEditor from "./code-editor.vue";
import {ref} from "vue";

type Doc = {
    type: string
    doc: string
    exp: string
};

@Component({components: {CodeEditor}})
class PaladinDoc extends Vue {
    @Prop docs: Array<Doc>

    sections = ref({
        shortcuts: true,
        operators: true
    });


    readonly shortcuts = [
        {keys: ['⇧ Shift', '↵ Enter'], action: 'Run cell'},
        {keys: ['Ctrl', '+'], action: 'Add a cell'},
        {keys: ['Ctrl', '-'], action: 'Remove a cell'},
        {keys: ['↑/↓'], action: 'Move between cells'},
        {keys: ['⌘ Command', 'K'], action: 'Open options menu'},
        {keys: ['Ctrl', '⇧ Shift', '-'], action: 'Collapse all cells'}
    ]

    midpoint: number
    columnOneShortcuts: Array<Object> = [];
    columnTwoShortcuts: Array<Object> = [];

    mounted() {
        this.midpoint = Math.ceil(this.shortcuts.length / 2);
        this.columnOneShortcuts = this.shortcuts.slice(0, this.midpoint);
        this.columnTwoShortcuts = this.shortcuts.slice(this.midpoint);
    }

    toggleSection(section: string) {
        this.sections[section] = !this.sections[section];
    }

    getCollapseIcon(section: string) {
        return this.sections[section] ? '➖' : '➕';
    }

    parseDoc(docString: string) {
        const lines = docString.split('\n');
        const operators = [];

        lines.forEach(line => {
            if (line.trim() === '') return; // Skip empty lines

            const operatorMatch = line.match(/^(\w+)\(([^)]*)\):\s+(.*)/);
            if (operatorMatch) {
                const [_, name, params, description] = operatorMatch;
                const paramList = params.split(',').map(p => p.trim());

                // Highlight the parameter references in the description
                let highlightedDescription = description;
                paramList.forEach(param => {
                    const regex = new RegExp(`\\b${param}\\b`, 'g'); // Word boundary to match whole words only
                    highlightedDescription = highlightedDescription.replace(regex, `<span class="operator-params">$&</span>`);
                });

                operators.push({
                    name,
                    params,
                    description: highlightedDescription
                });
            }
        });

        return operators;
    }


}

export default toNative(PaladinDoc);

</script>

<style lang="scss" scoped>

.cheat-sheet-container {
    background: #2b2b2b;
    color: #ccc;
    padding: 20px;
    font-family: 'Consolas', 'Courier New', monospace;
}

.cheat-sheet-title {
    color: #fff;
    text-align: center;
    margin-bottom: 30px;
}

.cheat-sheet-section {
    background: #1e1e1e;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
    color: #4caf50;
    margin-bottom: 10px;
}

.section-description {
    color: #bbb;
    margin-bottom: 10px;
}

.documentation .operator-block {
    margin-bottom: 5px; /* Spacing between operators */
}

.operator-name {
    color: #ffeb3b; /* Yellow for the operator name and parentheses */
    font-weight: bold;
}

.operator-params {
    color: #ff9800; /* Orange for parameters */
}

.operator-description {
    display: block; /* Description in new line */
}

.keyboard-key {
    display: inline-block;
    background-color: #fff;
    color: #000;
    text-align: center;
    border-radius: 3px;
    border: 1px solid #ccc;
    padding: 3px 5px;
    margin: 0 2px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.8rem;
    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
    user-select: none; /* Prevent text selection */
}

.shortcuts-list {
    list-style: none;
    padding: 0;
}

.shortcuts-list li {
    margin-bottom: 5px;
}

.shortcuts-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
}

.shortcuts-column {
    width: 48%; /* Adjust width for two columns */
}

.collapse-icon {
    cursor: pointer;
    display: inline-block;
    margin-right: 10px;
}

.cheat-sheet-section {
    margin-bottom: 20px;
}

.section-header {
    cursor: pointer;
    display: flex;
    align-items: center;
    user-select: none;
}
</style>