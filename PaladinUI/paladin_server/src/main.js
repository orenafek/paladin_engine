import Tree from "vue3-tree";
import * as Vue from "vue/dist/vue.esm-bundler.js";
import "codemirror/mode/python/python.js";
import "codemirror/theme/darcula.css";
import "codemirror/addon/scroll/simplescrollbars";
import "codemirror/addon/scroll/simplescrollbars.css";
import Codemirror from "codemirror-editor-vue3";
import {Splitpanes, Pane} from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

import {request_debug_info} from "./request"
import {capitalizeFirstLetter} from "./string_utils";
import Vue3Highlightjs from "./vue3-highlight";
import Highlighted, {escapeHTMLTags} from "./components/highlighted.vue";
import ArchiveTable from "./components/archive_entries_table.vue";
import tabular from "./components/tabular.vue";
import CustomizedPresentation from "./components/customized_presentation_code_editor.vue"
import {persistField, LocalStore} from "./infra/store";
import Slider from "@vueform/slider";
import "@vueform/slider/themes/default.scss";

import LoadingSpinner from "./components/loading_spinner.vue";
import './main.scss';
import Markdown from "vue3-markdown-it";


const DEFAULT_CUSTOMIZER = `def customizer(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Customize a row of results.
    @type d: Dict[str, Any]
    @param d: A dict in which the keys are the columns and the values are the row's 
            result in that column, i.e. {column: row[column]} 
    """ 
    return d
`;


const mainComponent = {
    components: {
        highlighted: Highlighted,
        archiveTable: ArchiveTable,
        Codemirror,
        Tree,
        loadingSpinner: LoadingSpinner,
        tabular,
        customizedPresentation: CustomizedPresentation,
        Markdown,
        Slider,
        Splitpanes, Pane
    },
    data: function () {
        return {
            layout: {
                panes: [{size: 30}]
            },
            exception_line_no: null,
            exception_line: null,
            exception_msg: null,
            exception_archive_time: null,
            source_code: [],
            line_no_to_debug: -1,
            archive_entries: [],
            archive_entries_columns: [],
            vars_to_follow: [],
            var_history: {},
            var_id_to_follow: null,
            line_to_debug: null,
            retrieved_objects: {},
            time_window: [],
            query: {
                select: "",
                startTime: 0,
                endTime: 10000,
                customizer: DEFAULT_CUSTOMIZER
            },
            queryInProgress: false,
            queryResult: {},
            dsl_docs: '',
            run_output: '',
            lastRunTime: 10000,
            runTimeWindow: [0, 10000],
            codemirror_options: {
                mode: "text/x-python",
                theme: "darcula",
                lineNumbers: false,
                smartIndent: true,
                indentUnit: 2,
                foldGutter: true,
                styleActiveLine: true,
                query_dsl_words: async () => (await request_debug_info("query_dsl_words")).join(", ")
            },
            codemirror_options_customizer: {
                mode: "text/x-python",
                theme: "darcula",
                lineNumbers: true,
                lineSeparator: '\n',
                smartIndent: true,
                indentUnit: 2
            },
            customizationCode: '',
            shouldCustomizeQuery: false
        }
    },
    created: async function () {
        this.source_code = await request_debug_info('source_code');
        const exception = await request_debug_info('exception_line');
        this.exception_line_no = exception != null ? exception['exception_line_no'] : null;
        this.exception_source_line = exception != null ? exception['exception_source_line'] : null;
        this.exception_msg = exception != null ? exception['exception_msg'] : null;
        this.exception_archive_time = exception != null ? exception['exception_archive_time'] : null;
        this.dsl_docs = (await request_debug_info('docs')).toString().trim();
        this.run_output = (await request_debug_info('run_output')).toString().trim();
        this.lastRunTime = parseInt((await request_debug_info('last_run_time')).toString());
        this.query.endTime = this.lastRunTime;
        this.runTimeWindow = [0, this.lastRunTime];
    },
    mounted() {
        persistField(this.query, 'select', new LocalStore('app:querySelect'));
        persistField(this.layout, 'panes', new LocalStore('app:layout.panes'));
        persistField(this.query, 'customizer', new LocalStore('app:queryCustomizer'));
    },
    compilerOptions: {
        delimiters: ['$$[', ']$$']
    },
    methods: {
        update_element_visibility: function (element_id, visibility) {
            document.getElementById(element_id).style.visibility = visibility ? 'visible' : 'hidden';
        },
        update_div_line_debug_visibility: function (visibility) {
            this.update_element_visibility('span_line_debug', visibility);
        },

        create_archive_entries_columns: async function (entries) {
            let columns = []
            if (entries.length > 0) {
                for (const entry_key in entries[0]) {
                    const isKey = entry_key === "time";
                    columns.push({
                        label: entry_key,
                        field: entry_key,
                        width: "3%",
                        sortable: true,
                        isKey: isKey
                    })
                }
            }
            this.archive_entries_columns = columns
        },

        select_line_no: async function (line_no) {
            this.line_no_to_debug = line_no;
            this.archive_entries = await request_debug_info('archive_entries', this.line_no_to_debug);
            this.archive_entries_columns = await this.create_archive_entries_columns(this.archive_entries);
            this.line_to_debug = await request_debug_info('source_code', this.line_no_to_debug);
            this.update_div_line_debug_visibility(true);
        },

        retrieve_object: async function (object_id, object_type, time) {
            this.retrieved_objects[object_id, time] = await request_debug_info('retrieve_object', object_id, object_type, time);
        },

        capitalize: capitalizeFirstLetter,

        create_time_window: async function () {
            const from = document.getElementById("time_window_from").value;
            const to = document.getElementById("time_window_to").value;

            this.time_window = await request_debug_info('time_window', from, to);
            this.update_element_visibility('time_window_archive_table', true);
        },

        run_query: async function () {
            this.queryInProgress = true;
            try {
                let resp = await request_debug_info("query",
                    ...[this.query.select, this.query.startTime, this.query.endTime,
                        this.shouldCustomizeQuery ? this.query.customizer : ""]);
                this.queryResult = JSON.parse(resp);
            } finally {
                this.queryInProgress = false;
            }
            return true;
        },

        formatResults(queryResult) {
            return {
                columnHeaders: queryResult['keys'],
                rowHeaders: Object.keys(queryResult).filter(k => k != 'keys')
                    .map(key => ({key, display: this.formatTimeInterval(key)})),
                rowData: queryResult
            };
        },

        formatTimeInterval(s) { return s.replace(/\((\d+), (\d+)\)/, '$1–$2'); },

        narrowTimeRange({rowHead}) {
            console.log(rowHead);
            let mo = rowHead.key.match(/\((\d+), (\d+)\)/);
            if (mo) {
                this.runTimeWindow = [parseInt(mo[1]), parseInt(mo[2])];
                this.sliderChange(this.runTimeWindow);
            }
        },

        update_customization_code: async function (code) {
            this.customizationCode = code;
        },

        store_layout_panes(ev) {
            this.layout.panes = ev.map(x => ({size: x.size}));
        },

        sliderChange(sliderValue) {
            this.query.startTime = sliderValue[0];
            this.query.endTime = sliderValue[1];
        },

        shouldCustomizeChange(_) {
            const isShouldCustomizeChecked = document.getElementById('shouldCustomize').checked;
            document.getElementById('customizeCollapsable').hidden = !isShouldCustomizeChecked;
            this.shouldCustomizeQuery = isShouldCustomizeChecked;
        }
    }

}

document.addEventListener("DOMContentLoaded", () => {
    const appProto = Vue.createApp(mainComponent)
        .use(Vue3Highlightjs)
        .use(Markdown);
    window.app = appProto.mount('#app');
    escapeHTMLTags();
});

