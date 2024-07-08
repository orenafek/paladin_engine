<template>
    <div class="code-editor-container">
        <div @mouseenter="() => {panelActive = true;}" @mouseleave="() => {panelActive = false;}">
            <Codemirror id="source-editor" ref="cm" class="original-style" :value="sourceCode"
                        :options="codemirrorOptions" @change="updateSourceCode"/>
        </div>
    </div>
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
    emits: ['code-editor-change', 'code-editor-reset']
})
class CodeEditor extends Vue {
    @Prop sourceCode: string
    @Prop originalSourceCode: string
    @Prop lang: string = ''
    @Prop actions: Array<any> = []

    codemirrorOptions = {theme: 'darcula', scrollbarStyle: 'overlay', styleActiveLine: true}
    _sourceCode: string = ''

    panelActive: boolean = false;
    panelPosition: { top: string, left: string } = {top: '0px', left: '0px'}

    @Ref cm: typeof Codemirror

    mounted() {
        this.codemirrorOptions['mode'] = this.lang;
        this._sourceCode = this.sourceCode;
        this.updatePanelPosition();
    }

    async btnAction(index: number) {
        await this.actions[index]?.action(this._sourceCode, this.originalSourceCode);
    }

    updateSourceCode($) {
        this._sourceCode = $;
        if (this._sourceCode === this.sourceCode) {
            /* If back to original */
            this.$emit('code-editor-reset');
        } else {
            this.$emit('code-editor-change');
        }
    }

    updatePanelPosition() {
        const codeEditorEl = this.cm.$el;
        const codeEditorRect = codeEditorEl.getBoundingClientRect();
        const panelWidth = 200; // Adjust this width according to your panel's width

        this.panelPosition = {
            top: codeEditorRect.top.toString() + 'px',
            left: (codeEditorRect.right / 2 + 30).toString() + 'px' // Adjust the offset as needed
        };
    };


    highlightRow(lineNumber: number): void {
        this.handleHighlighting(lineNumber, true);
    }

    unHighlightRow(lineNumber: number): void {
        this.handleHighlighting(lineNumber, false);
    }

    private handleHighlighting(lineNumber: number, highlight: boolean) {
        const editor = this.cm.cminstance;

        /*  Decrease one from line number as the lines in codemirror starts at 1. */
        lineNumber = lineNumber - 1;

        if (highlight){
            /* Set active line. */
            editor.operation(() => {
                const pos = {line: lineNumber, ch: 'end', margin: 3};
                editor.setCursor(pos);
                editor.scrollIntoView(pos);
            });
        }

        editor.operation(() => {
             /* Set background color. */
            const lineElement = this.lineNo2Element(editor, lineNumber);
            console.log('le = ', lineElement);
            if (lineElement) {
                lineElement.style.backgroundColor = highlight ? 'yellow' : '';
            }
        });
    }

    private lineNo2Element(editor, lineNumber): HTMLElement {
        const lineElements: Array<HTMLElement> = editor.getWrapperElement().getElementsByClassName('CodeMirror-line');
        console.log('les = ', lineElements, ' ln = ', lineNumber);
        return lineElements[lineNumber];
    }

    height(): number {
        return this.cm.cminstance.getScrollerElement().clientHeight;
    }

    get source(): string {
        return this._sourceCode;
    }
}

export default toNative(CodeEditor);

</script>

<style lang="scss" scoped>
.code-editor-container {
    background-color: #2b2b2b;
    height: 100%;
    width: 100%;
}

.code-editor-container::-webkit-scrollbar {
    background-color: #2b2b2b;
}

.CodeMirror-activeline-background {
    background: #f3c014;
}

.highlighted-line {
    background: #f3c014;
}

</style>