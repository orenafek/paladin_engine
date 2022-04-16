import {request_debug_info} from "./request"
import {capitalizeFirstLetter} from "./string_utils";
import Tree from "vue3-tree";
import * as Vue from "vue/dist/vue.esm-bundler.js";
import Vue3Highlightjs from "./vue3-highlight";
import Highlighted from "./components/highlighted.vue";
import {escapeHTMLTags} from "./components/highlighted.vue";
import ArchiveTable from "./components/archive_entries_table.vue";
import TableLite from "vue3-table-lite";

const debug_info = {
    components: {
        highlighted: Highlighted,
        archiveTable: ArchiveTable,
        Tree
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
            time_window: []
        }
    },
    created: async function () {
        this.source_code = await request_debug_info('source_code');
        const exception = await request_debug_info('exception_line');
        this.exception_line_no = exception != null ? exception['exception_line_no'] : null;
        this.exception_source_line = exception != null ? exception['exception_source_line'] : null;
        this.exception_msg = exception != null ? exception['exception_msg'] : null;
        this.exception_archive_time = exception != null ? exception['exception_archive_time'] : null;
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
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const debug_info_vue_app = Vue.createApp(debug_info);
    debug_info_vue_app.use(Vue3Highlightjs);
    debug_info_vue_app.mount('#header');
    escapeHTMLTags();
});

