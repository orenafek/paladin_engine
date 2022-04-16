import {request} from "./request"
import {capitalizeFirstLetter} from "./string_utils";
import Tree from "vue3-tree";
import * as Vue from "vue/dist/vue.esm-bundler.js";
import Vue3Highlightjs from "./vue3-highlight";
import {ref} from "vue";
import Highlighted from "./components/highlighted.vue";
import {escapeHTMLTags} from "./components/highlighted.vue";
import archive_entries_table from "./components/archive_entries_table.vue";

const debug_info = {
    components: {
        highlighted: Highlighted,
        ArchiveTable: archive_entries_table,
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
            vars_to_follow: [],
            var_history: {},
            var_id_to_follow: null,
            line_to_debug: null,
            retrieved_objects: {},
            time_window: null
        }
    },
    created: async function () {
        this.source_code = (await request('debug_info', {'info': 'source_code'}))['result']['source_code'];
        const exception = (await request('debug_info', {'info': 'exception_line'}))['result'];
        this.exception_line_no = exception != null ? exception['exception_line_no'] : null;
        this.exception_line = exception != null ? exception['exception_line'] : null;
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
            this.update_element_visibility('div_line_debug', visibility);
        },

        update_div_followed_var_history_visibility: function (visibility) {
            this.update_element_visibility('div_followed_var_history', visibility);
        },

        select_line_no: async function (line_no) {
            this.line_no_to_debug = line_no;
            this.archive_entries = new Object(
                (await request('debug_info',
                    {
                        'line_no_to_debug': this.line_no_to_debug,
                        'info': 'archive_entries'
                    }
                ))['result']['archive_entries']);
            this.vars_to_follow = new Object(
                (await request('debug_info',
                    {
                        'line_no_to_debug': this.line_no_to_debug,
                        'info': 'vars_to_follow'
                    }))['result']['vars_to_follow']);
            this.line_to_debug = new Object(await request('debug_info',
                {
                    'line_no': this.line_no_to_debug,
                    'info': 'get_line'
                }))['result']['line'];

            this.update_div_line_debug_visibility(true);
            this.update_div_followed_var_history_visibility(false);
        },

        follow_var: async function (event) {
            const clicked_button_key = event.target.id;
            this.var_history[clicked_button_key] = new Object(
                (await request('debug_info',
                    {
                        'info': 'var_assignments',
                        'var_id_to_follow': clicked_button_key.toString()
                    }))['result']['var_assignments']);
            this.var_id_to_follow = clicked_button_key;
            this.update_div_followed_var_history_visibility(true);
        },

        retrieve_object: async function (object_id, object_type, time) {
            this.retrieved_objects[object_id, time] = new Object((await request('debug_info',
                {
                    'info': 'retrieve_object',
                    'object_id': object_id,
                    'object_type': object_type,
                    'time': time
                }))['result']['object']);
        },

        objectLifetime: async function (object_id) {
            this.var_history[object_id] = new Object((await request('debug_info',
                {'info': 'object_lifetime', 'object_id': object_id}))['result']['lifetime']);
            this.var_id_to_follow = object_id;
            console.log(this.var_history[object_id]);
            this.var_history[object_id] = this.example_nodes;
            this.update_div_followed_var_history_visibility(true);
        },

        capitalize: capitalizeFirstLetter,

        source_code_hover_event: function (id) {
            document.getElementById(id).style.textDecoration = 'underline';
        },

        create_time_window: async function (from, to) {
            this.time_window = new Object((await request('debug_info',
                {
                    'info': "get_time_window",
                    'from': from,
                    'to': to
                }))['result']['time_window']);
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

