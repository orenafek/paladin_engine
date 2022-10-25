import Tree from "vue3-tree";
import * as Vue from "vue/dist/vue.esm-bundler.js";
import "codemirror/mode/python/python.js";
import "codemirror/theme/darcula.css";
import "codemirror/addon/scroll/simplescrollbars";
import "codemirror/addon/scroll/simplescrollbars.css";
import Codemirror from "codemirror-editor-vue3";
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

import {request_debug_info} from "./request"
import {capitalizeFirstLetter} from "./string_utils";
import Vue3Highlightjs from "./vue3-highlight";
import Highlighted, {escapeHTMLTags} from "./components/highlighted.vue";
import ArchiveTable from "./components/archive_entries_table.vue";
import tabular from "./components/tabular.vue";
import { persistField, LocalStore } from "./infra/store";

import LoadingSpinner from "./components/loading_spinner.vue";
import './main.scss';
import Markdown from "vue3-markdown-it";

const mainComponent = {
    components: {
        highlighted: Highlighted,
        archiveTable: ArchiveTable,
        Codemirror,
        Tree,
        loadingSpinner: LoadingSpinner,
        tabular,
        Markdown,
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
            last_time: -1,
            query: {
                select: "",
                startTime: 0,
                endTime: 10000,
                lineNo: 0
            },
            queryInProgress: false,
            queryResult: {},
            dsl_docs: '',
            codemirror_options: {
                mode: "text/x-python",
                theme: "darcula",
                lineNumbers: false,
                smartIndent: true,
                indentUnit: 2,
                foldGutter: true,
                styleActiveLine: true,
                query_dsl_words: async () => (await request_debug_info("query_dsl_words")).join(", ")
            }
        }
    },
    created: async function () {
        this.source_code = await request_debug_info('source_code');
        const exception = await request_debug_info('exception_line');
        this.exception_line_no = exception != null ? exception['exception_line_no'] : null;
        this.last_time = await request_debug_info('last_time');
        document.getElementById('query_end_time').innerText = this.last_time;
        this.exception_source_line = exception != null ? exception['exception_source_line'] : null;
        this.exception_msg = exception != null ? exception['exception_msg'] : null;
        this.exception_archive_time = exception != null ? exception['exception_archive_time'] : null;
        this.dsl_docs = (await request_debug_info('docs')).toString().trim();
    },
    mounted() {
        persistField(this, 'query', new LocalStore('app:query'));
        persistField(this.layout, 'panes', new LocalStore('app:layout.panes'));
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
                this.queryResult = await request_debug_info("query",
                    ...[this.query.select,
                        this.query.startTime, this.query.endTime, this.query.lineNo]);
            }
            finally {
                this.queryInProgress = false;
            }
            return true;
        },

        store_layout_panes(ev) {
            this.layout.panes = ev.map(x => ({size: x.size}));
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

