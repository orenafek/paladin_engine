import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import *

from flask import Flask, render_template, request, send_file
from flask_classful import FlaskView, route
from flask_cors import CORS

from PaladinEngine.engine.engine import PaLaDiNEngine
from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator, QUERY_DSL_WORDS
from archive.archive_evaluator.paladin_dsl_parser import PaladinDSLParser
from common.common import ISP

NAME = 'PaLaDiN Debug Server'
TEMPLATE_FOLDER = Path.cwd().joinpath('interactive_graph').joinpath('templates')
STATIC_FOLDER = Path.cwd().joinpath('interactive_graph').joinpath('static')
SCRIPTS_FOLDER = STATIC_FOLDER.joinpath('scripts')
STYLES_FOLDER = STATIC_FOLDER.joinpath('styles')
JSON_FILE_NAME = 'input_graph_tree.json'
SOURCE_CODE: str = ''
EVALUATOR: Optional[ArchiveEvaluator] = None
ARCHIVE: Optional[Archive] = None

# FIXME: Currently for debugging purposes.
THROWN_EXCEPTION: Optional[PaLaDiNEngine.PaladinRunExceptionData] = None


class PaladinDebugServer(FlaskView):
    @dataclass
    class _ArchiveEntriesView(object):
        stub: str
        container_id: int
        field: str
        expression: str
        value: object
        type: type
        time: int

    @dataclass
    class _VarHistoryView(object):
        field: str
        value: object
        line_no: int
        expression: str
        time: int

    @classmethod
    def create(cls, source_code: str,
               archive: Archive,
               thrown_exception: Optional[Tuple[int, str]] = None) -> 'PaladinDebugServer':
        global SOURCE_CODE, THROWN_EXCEPTION, ARCHIVE, EVALUATOR
        server = PaladinDebugServer()
        SOURCE_CODE = source_code
        THROWN_EXCEPTION = thrown_exception
        ARCHIVE = archive
        EVALUATOR = ArchiveEvaluator(ARCHIVE)
        return server

    def run(self, port: int = 9999):
        self.register_app()
        self.app.run(port=port)

    def __init__(self):
        self._app = Flask(NAME, template_folder=str(TEMPLATE_FOLDER), static_folder=str(STATIC_FOLDER))
        self._app.jinja_options['variable_start_string'] = '@='
        self._app.jinja_options['variable_end_string'] = '=@'
        CORS(self.app, resources={r'/*': {'origins': '*'}})

    def register_app(self):
        self.app.template_folder = TEMPLATE_FOLDER
        PaladinDebugServer.register(self.app, route_base='/')

    @property
    def app(self):
        return self._app

    @classmethod
    def create_response(cls, data: object):
        caller = sys._getframe().f_back.f_code.co_name
        return {'result': {caller: data}}

    @route('/', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'GET':
            return render_template('index.html')
        if request.method == 'POST':
            return self.search()

    @route('/debug', methods=['GET', 'POST'])
    def debug(self):
        if request.method == 'GET':
            return render_template('debug.html')

    @route('/input_graph_tree.json')
    def input_graph_tree(self):
        with open(os.path.join(TEMPLATE_FOLDER, JSON_FILE_NAME), 'r') as f:
            return f.read()

    @route('/scripts/<string:path>')
    def get_script(self, path):
        return send_file(str(SCRIPTS_FOLDER.joinpath(path)), 'text/javascript')

    @route('/styles/<string:path>')
    def get_stylesheet(self, path):
        return send_file(str(STYLES_FOLDER.joinpath(path)), 'text/css')

    @route('/debug_info/source_code')
    @route('/debug_info/source_code/<int:line>')
    def source_code(self, line: int = None):
        return PaladinDebugServer.create_response(
            SOURCE_CODE.split('\n') if not line
            else PaladinDebugServer._get_line_from_source_code(line))

    @route('/debug_info/exception_line')
    def exception_line(self):
        return PaladinDebugServer.create_response({'exception_line_no': THROWN_EXCEPTION.source_code_line_no,
                                                   'exception_source_line': THROWN_EXCEPTION.source_line,  # TODO: Huh?
                                                   'exception_msg': THROWN_EXCEPTION.exception_msg,
                                                   'exception_archive_time': THROWN_EXCEPTION.archive_time}
                                                  if THROWN_EXCEPTION else {})

    @route('/debug_info/archive_entries/<int:line_no>')
    def archive_entries(self, line_no: int):
        return PaladinDebugServer.create_response(
            PaladinDebugServer._present_archive_entries(ARCHIVE.get_by_line_no(line_no).items()))

    @route('/debug_info/vars_to_follow/<int:line_no>')
    def vars_to_follow(self, line_no: int):
        archive_entries: list = PaladinDebugServer._present_archive_entries(ARCHIVE.get_by_line_no(line_no).items())

        @dataclass
        class _ArchiveVarView(object):
            container_id: int
            id: str
            field: int
            value: object

            def __hash__(self):
                return hash(hash(self.id) + hash(self.field) + hash(self.value))

        return PaladinDebugServer.create_response(list(
            {_ArchiveVarView(aev.container_id, aev.value if type(aev.value) is str else str(aev.value), aev.field,
                             ARCHIVE.search_web(aev.field)) for aev in archive_entries}))

    @route('/debug_info/var_assignments/<int:var_id>')
    def var_assignments(self, var_id: int):
        return PaladinDebugServer.create_response([PaladinDebugServer._VarHistoryView(
            key.field,
            value.value,
            value.line_no,
            value.expression,
            value.time
        ) for (key, value_list) in ARCHIVE.get_by_container_id(var_id).items() for value in value_list])

    @route('/debug_info/object_lifetime/<int:obj_id>')
    def object_lifetime(self, obj_id: int):
        lifetime = ARCHIVE.object_lifetime(obj_id)

        def convert_object_state_to_node(i: int, object_state: Union[Dict, object]) -> Tuple[int, Union[List, Dict]]:
            if type(object_state) is not dict:
                return i + 1, {'id': i, 'label': str(object_state)}
            return i + 1, [
                {'id': i, 'label': field, 'nodes': convert_object_state_to_node(i + 1, object_state[field])[1]} for
                field in object_state]

        nodes = []
        i = 1
        for time, state in lifetime.items():
            j, state_tree = convert_object_state_to_node(i + 1, state)
            nodes.append({'id': i, 'label': time, 'nodes': state_tree})
            i = j

        return PaladinDebugServer.create_response(nodes)

    @route('/debug_info/time_window/<int:from_time>/<int:to>')
    def time_window(self, from_time: int, to: int):
        return PaladinDebugServer.create_response(
            PaladinDebugServer._present_archive_entries(
                ARCHIVE.get_all_assignments_in_time_range(from_time, to).items()))

    @route('/debug_info/query/<string:select_query>/<int:start_time>/<int:end_time>/<int:line_no>',
           defaults={'where_query': ''})
    @route('/debug_info/query/<string:select_query>/<string:where_query>/<int:start_time>/<int:end_time>/<int:line_no>')
    def query(self, select_query: str, where_query: str, start_time: int, end_time: int, line_no: int):
        pdslp = PaladinDSLParser.create(ARCHIVE, start_time, end_time, line_no)
        return PaladinDebugServer.create_response(pdslp.parse_and_summarize(select_query, where_query))

    @route('/debug_info/query_dsl_words')
    def query_dsl_words(self):
        return PaladinDebugServer.create_response(QUERY_DSL_WORDS)

    @route('/debug_info', methods=['POST'])
    def debug_info(self):
        args = request.json['args']
        response = {}
        if 'info' in args:
            if args['info'] == 'retrieve_object':
                response = {
                    'object': ARCHIVE.retrieve_value(int(args['object_id']), args['object_type'], int(args['time']))}
        return {'result': response}

    @route('/source_code.txt')
    def src_code(self):
        return SOURCE_CODE

    @staticmethod
    def _get_line_from_source_code(line_no: int) -> str:
        if line_no <= 0:
            return ''

        return SOURCE_CODE.split('\n')[line_no - 1].strip()

    @route('/search', methods=['POST'])
    def search(self):
        if not request.json:
            result = {'search_result': ''}
        else:
            result = {'search_result': ARCHIVE.search_web(request.json['expression_to_search'])}
        return result

    @staticmethod
    def _present_archive_entries(archive_entries) -> List['PaladinDebugServer._ArchiveEntriesView']:
        return sorted([
            PaladinDebugServer._ArchiveEntriesView(
                key.stub_name,
                key.container_id,
                key.field,
                value.expression,
                value.value if ISP(value.value) else str(value.value),
                value.rtype.__name__ if ISP(value.rtype) else 'ptr',
                value.time
            ) for (key, value_list) in archive_entries for value in value_list
        ], key=lambda aev: aev.time, reverse=True)
