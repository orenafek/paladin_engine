import {request_debug_info} from "./request"
import {capitalizeFirstLetter} from "./string_utils";
import Tree from "vue3-tree";
import * as Vue from "vue/dist/vue.esm-bundler.js";
import Vue3Highlightjs from "./vue3-highlight";
import Highlighted, {escapeHTMLTags} from "./components/highlighted.vue";
import ArchiveTable from "./components/archive_entries_table.vue";
import Codemirror from "codemirror-editor-vue3";
import {CodeMirror} from "codemirror-editor-vue3";

import "codemirror/mode/python/python.js";
import "codemirror/theme/darcula.css";
import tabular from "./components/tabular.vue";

const debug_info = {
    components: {
        highlighted: Highlighted,
        archiveTable: ArchiveTable,
        Codemirror,
        Tree,
        tabular
    },
    data: function () {
        return {
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
            query_select: "",
            query_where: "",
            query_start_time: 0,
            query_end_time: 0,
            query_line_no: 0,
            tabular_query_result: {},
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
        this.exception_source_line = exception != null ? exception['exception_source_line'] : null;
        this.exception_msg = exception != null ? exception['exception_msg'] : null;
        this.exception_archive_time = exception != null ? exception['exception_archive_time'] : null;
        if (localStorage['AppQuery']) {
            Object.assign(this, JSON.parse(localStorage['AppQuery']));
        }

        window.addEventListener("beforeunload", () => {
            localStorage['AppQuery'] = JSON.stringify(Object.fromEntries(Object.entries(this.$data).filter(([k, v]) => k.startsWith("query_"))));
        });
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
            const query_result = await request_debug_info("query",
                ...[this.query_select, this.query_where !== "" ? this.query_where : "True",
                    this.query_start_time, this.query_end_time, this.query_line_no]);

            this.tabular_query_result = query_result;

            document.getElementById("query_result").value =
                Object.keys(query_result).length > 0 ? JSON.stringify(query_result) : "No faults in lines.";
        },

        onQuerySelectChange: function (val, cm) {
            //this.query_select = val != null ? val : "";
        },
        onQueryWhereChange: function (val, cm) {
            //this.query_where = val != null && val !== "" ? val : "";
        }
    }

}

document.addEventListener("DOMContentLoaded", () => {
    const debug_info_vue_app = Vue.createApp(debug_info);
    debug_info_vue_app.use(Vue3Highlightjs);
    window.app = debug_info_vue_app.mount('#header');
    escapeHTMLTags();
});

