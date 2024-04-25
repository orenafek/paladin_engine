<template>
    <div class="panel-container">
        <div class="panel">
            <va-button v-for="(action, index) in actions" color="#eb6734" :icon="action.icon"
                       :style="`'grid-column: ${index}`"
                       @click="btnAction(index)">{{ action.name }}
            </va-button>
        </div>
    </div>
    <Codemirror id="source-editor" ref="cm" class="original-style" :value="sourceCode"
                :options="codemirrorOptions" @change="updateSourceCode"/>
</template>

<script lang="ts">
import {Component, Prop, Ref, toNative, Vue} from "vue-facing-decorator";

/* Codemirror imports */
import "codemirror/mode/python/python.js";
import "codemirror/theme/darcula.css";
import "codemirror/addon/scroll/simplescrollbars";
import "codemirror/addon/scroll/simplescrollbars.css";
import Codemirror from "codemirror-editor-vue3";
import "./main.scss";

@Component({
    components: {Codemirror},
})
class CodeEditor extends Vue {
    @Prop sourceCode: string
    @Prop lang: string = ''
    @Prop actions: Array<any> = []

    codemirrorOptions = {theme: 'darcula', scrollbarStyle: 'overlay'}
    /* TODO: Can this be removed? */
    _sourceCode: string = ''

    @Ref cm: typeof Codemirror

    mounted() {
        this.codemirrorOptions['mode'] = this.lang;
        this._sourceCode = this.sourceCode;
    }

    async btnAction(index: number) {
        await this.actions[index]?.action(this._sourceCode);
    }

    updateSourceCode($) {
        this._sourceCode = $;
    }

    highlightRow(lineNumber: number): void {
        this.handleHighlighting(lineNumber, true);
    }

    unHighlightRow(lineNumber: number): void {
        this.handleHighlighting(lineNumber, false);
    }

    private handleHighlighting(lineNumber: number, highlight: boolean) {
        const editor = this.cm.cminstance;
        const className = "code-editor-highlighted-row";

        /*  Decrease one from line number as the lines in codemirror starts at 1. */
        lineNumber = lineNumber - 1;

        editor.operation(() => {
            const pos = {line: lineNumber, ch: 'end', margin: 3};
            editor.setCursor(pos);
            editor.scrollIntoView(pos);
        });

        editor.operation(() => {
            if (highlight) {
                editor.addLineClass(lineNumber, 'background', className);
            } else {
                editor.removeLineClass(lineNumber, 'background', className);
            }
        });

       this.addHighlightStyles(className);
    }

    private addHighlightStyles(className: string): void {
        const styleElements: HTMLCollectionOf<HTMLStyleElement> = document.head.getElementsByTagName('style');

        if (!Array.from(styleElements).some((styleElement: HTMLStyleElement) => styleElement.innerHTML.includes(`.$ {className}`))) {
            const styleTag = document.createElement('style');
            // language=CSS
            styleTag.textContent = `.${className} {
                background-color: yellow
            }`;
            document.head.appendChild(styleTag);
        }
    }
}

export default toNative(CodeEditor);

</script>

<style lang="scss" scoped>

.grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 25px;
}

.panel-container {
    background: #282727;
    padding: 8px;
}

.panel {
    @extend .grid-container;
    max-width: 450px;
}

.btn {
    grid-column: var(--idx);
}

</style>