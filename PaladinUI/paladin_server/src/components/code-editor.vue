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

    highlightRow(lineNumber) {
        const editor = this.cm.cminstance;
        const className = "code-editor-highlighted-row";
        let flashingInterval;
        let flashingDuration = 2000; // Flashing duration in milliseconds
        let hasLineClass = false;

        /*  Decrease one from line number as the lines in codemirror starts at 1. */
        lineNumber = lineNumber - 1;

        // // Scroll the highlighted line into view

        editor.operation(() => {
            const lineHandle = editor.getLineHandle(lineNumber);
            console.log('lineHandle = ', lineHandle);
            const pos = {line: lineNumber, ch: 'end', margin: 3};
            editor.setCursor(pos);
            editor.scrollIntoView(pos);
        });


        const toggleHighlight = () => {
            editor.operation(() => {
                if (hasLineClass) {
                    editor.removeLineClass(lineNumber, 'background', className);
                    hasLineClass = false;
                } else {
                    editor.addLineClass(lineNumber, 'background', className);
                    hasLineClass = true;
                }
            });
        };

        // Start flashing
        flashingInterval = setInterval(toggleHighlight, 500); // Toggle every 500 milliseconds

        // Stop flashing after the specified duration
        setTimeout(() => {
            clearInterval(flashingInterval);
            editor.removeLineClass(lineNumber, 'background', className);
        }, flashingDuration);


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