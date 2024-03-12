import sys
from dataclasses import dataclass
from pathlib import Path
from typing import *

from flask import Flask, request, send_file, send_from_directory
from flask_classful import FlaskView, route
from flask_cors import CORS

from PaladinEngine.engine.engine import PaLaDiNEngine
from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator
from archive.archive_evaluator.paladin_dsl_semantics import Operator
from archive.archive_evaluator.paladin_native_parser import PaladinNativeParser
from archive.object_builder.naive_object_builder.naive_object_builder import NaiveObjectBuilder
from archive.object_builder.recursive_object_builder.recursive_object_builder import RecursiveObjectBuilder
from common.common import ISP

NAME = 'PaLaDiN - Time-travel Debugging with Semantic Queries'
HERE = Path(__file__).parent
TEMPLATE_FOLDER = HERE / 'templates'
STATIC_FOLDER = HERE / 'static'
UPLOAD_FOLDER = HERE / 'upload'
SCRIPTS_FOLDER = STATIC_FOLDER / 'scripts'
STYLES_FOLDER = STATIC_FOLDER / 'styles'
ICONS_FOLDER = STATIC_FOLDER / 'icons'
JSON_FILE_NAME = 'input_graph_tree.json'

ENGINE: Optional[PaLaDiNEngine] = None
RUN_DATA: Optional[PaLaDiNEngine.PaladinRunData] = None
EVALUATOR: Optional[ArchiveEvaluator] = None
PARSER: Optional[PaladinNativeParser] = None


class PaladinServer(FlaskView):
    @dataclass
    class _ArchiveEntriesView(object):
        stub: str
        container_id: int
        field: str
        line_no: int
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
    def create(cls, engine: PaLaDiNEngine) -> 'PaladinServer':
        global ENGINE, RUN_DATA, EVALUATOR, PARSER
        server = PaladinServer()
        server._reset(engine)
        return server

    def run(self, port: int = 9999):
        self.register_app()
        self.app.run(port=port)

    @classmethod
    def _reset(cls, engine: PaLaDiNEngine):
        global ENGINE, RUN_DATA, EVALUATOR, PARSER
        ENGINE = engine
        RUN_DATA = engine.run_data
        RUN_DATA.archive.global_map = ENGINE.global_map
        EVALUATOR = ArchiveEvaluator(RUN_DATA.archive)
        PARSER = PaladinNativeParser(RUN_DATA.archive)
        #PARSER = PaladinNativeParser(RUN_DATA.archive, object_builder_type=RecursiveObjectBuilder)
        #PARSER = PaladinNativeParser(RUN_DATA.archive, object_builder_type=NaiveObjectBuilder)

    def __init__(self):
        self._app = Flask(NAME, template_folder=str(TEMPLATE_FOLDER), static_folder=str(STATIC_FOLDER))
        self._app.jinja_options['variable_start_string'] = '@='
        self._app.jinja_options['variable_end_string'] = '=@'
        self._app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
        CORS(self.app, resources={r'/*': {'origins': '*'}})

    def register_app(self):
        self.app.template_folder = TEMPLATE_FOLDER
        PaladinServer.register(self.app, route_base='/')

    @property
    def app(self):
        return self._app

    @classmethod
    def create_response(cls, data: object):
        caller = sys._getframe().f_back.f_code.co_name
        return {'result': {caller: data}}

    @route('/', methods=['GET', 'POST'])
    def debug(self):
        if request.method == 'GET':
            return send_from_directory(TEMPLATE_FOLDER, 'index.html')

    @route('/favicon.ico')
    def favicon(self):
        return send_from_directory(ICONS_FOLDER, 'favicon.ico')

    @route('/graph', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'GET':
            return send_from_directory(TEMPLATE_FOLDER, 'graph.html')
        if request.method == 'POST':
            return self.search()

    @route('/rerun')
    def rerun(self):
        ENGINE.execute_with_paladin()
        PaladinServer._reset(ENGINE)
        return PaladinServer.create_response({})

    @route('/scripts/<string:path>')
    def get_script(self, path):
        return send_file(SCRIPTS_FOLDER / path, 'text/javascript')

    @route('/styles/<string:path>')
    def get_stylesheet(self, path):
        return send_file(STYLES_FOLDER / path, 'text/css')

    @route('/debug_info/source_code')
    @route('/debug_info/source_code/<int:line>')
    def source_code(self, line: int = None):
        return PaladinServer.create_response(
            ENGINE.source_code.split('\n') if not line
            else PaladinServer._get_line_from_source_code(line))

    @route('/upload/source_code', methods=['POST'])
    def upload_source_code(self):
        ENGINE.update_source_code(request.get_data(as_text=True))
        return PaladinServer.create_response({})

    @route('/debug_info/thrown_exception')
    def thrown_exception(self):
        return PaladinServer.create_response(
            ENGINE.run_data.thrown_exception.as_dict if ENGINE.run_data.thrown_exception is not None else {})

    @route('/debug_info/archive_entries/<int:line_no>')
    def archive_entries(self, line_no: int):
        return PaladinServer.create_response(
            PaladinServer._present_archive_entries(RUN_DATA.archive.get_by_line_no(line_no).items()))

    @route('/debug_info/vars_to_follow/<int:line_no>')
    def vars_to_follow(self, line_no: int):
        archive_entries: list = PaladinServer._present_archive_entries(RUN_DATA.archive.get_by_line_no(line_no).items())

        @dataclass
        class _ArchiveVarView(object):
            container_id: int
            id: str
            field: int
            value: object

            def __hash__(self):
                return hash(hash(self.id) + hash(self.field) + hash(self.value))

        return PaladinServer.create_response(list(
            {_ArchiveVarView(aev.container_id, aev.value if type(aev.value) is str else str(aev.value), aev.field,
                             RUN_DATA.archive.search_web(aev.field)) for aev in archive_entries}))

    @route('/debug_info/var_assignments/<int:var_id>')
    def var_assignments(self, var_id: int):
        return PaladinServer.create_response([PaladinServer._VarHistoryView(
            key.field,
            value.value,
            value.line_no,
            value.expression,
            value.time
        ) for (key, value_list) in RUN_DATA.archive.get_by_container_id(var_id).items() for value in value_list])

    @route('/debug_info/object_lifetime/<int:obj_id>')
    def object_lifetime(self, obj_id: int):
        lifetime = RUN_DATA.archive.object_lifetime(obj_id)

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

        return PaladinServer.create_response(nodes)

    @route('/debug_info/last_run_time')
    def last_run_time(self):
        return PaladinServer.create_response(RUN_DATA.archive.last_time)

    @route('/debug_info/time_window/<int:from_time>/<int:to>')
    def time_window(self, from_time: int, to: int):
        return PaladinServer.create_response(
            PaladinServer._present_archive_entries(
                RUN_DATA.archive.get_assignments(from_time, to).items()))

    @route('/debug_info/completions')
    def completions(self):
        return PaladinServer.create_response(
            [{'label': op.name(), 'type': 'keyword', 'info': op.__doc__} for op in Operator.all()]
        )

    @route('/debug_info/query/<string:select_query>/<int:start_time>/<int:end_time>/', defaults={'customizer': ''})
    @route('/debug_info/query/<string:select_query>/<int:start_time>/<int:end_time>/<string:customizer>')
    def query(self, select_query: str, start_time: int, end_time: int, customizer: str):
        return PaladinServer.create_response(
            PARSER.parse(select_query.replace('<br>', '\n'), start_time, end_time,
                         customizer=customizer.replace('<br>', '\n')))

    @route('/uploader', methods=['GET', 'POST'])
    def upload_file(self):
        if request.method == 'POST':
            f = request.data
            PARSER.add_user_aux(f)
            return PaladinServer.create_response({})

    @route('/reset_aux_file')
    def reset_aux_file(self):
        PARSER.remove_user_aux()
        return PaladinServer.create_response({})

    @route('/debug_info/docs')
    def docs(self):
        return PaladinServer.create_response(PaladinNativeParser.docs())

    @route('/debug_info/run_output')
    def run_output(self):
        return PaladinServer.create_response(RUN_DATA.output)

    @route('/debug_info', methods=['POST'])
    def debug_info(self):
        args = request.json['args']
        response = {}
        if 'info' in args:
            if args['info'] == 'retrieve_object':
                response = {
                    'object': RUN_DATA.archive.retrieve_value(int(args['object_id']), args['object_type'],
                                                              int(args['time']))}
        return {'result': response}

    @route('/source_code.txt')
    def src_code(self):
        return ENGINE.source_code

    @staticmethod
    def _get_line_from_source_code(line_no: int) -> str:
        if line_no <= 0:
            return ''

        return ENGINE.source_code.split('\n')[line_no - 1].strip()

    @route('/search', methods=['POST'])
    def search(self):
        if not request.json:
            result = {'search_result': ''}
        else:
            result = {'search_result': RUN_DATA.archive.search_web(request.json['expression_to_search'])}
        return result

    @staticmethod
    def _present_archive_entries(archive_entries) -> List['PaladinServer._ArchiveEntriesView']:
        return sorted([
            PaladinServer._ArchiveEntriesView(
                key.stub_name,
                key.container_id,
                key.field,
                value.line_no,
                value.expression,
                value.value if ISP(value.value) else str(value.value),
                value.rtype.__name__ if ISP(value.rtype) else 'ptr',
                value.time
            ) for (key, value_list) in archive_entries for value in value_list
        ], key=lambda aev: aev.time, reverse=True)

    @staticmethod
    def _run_time_window():
        return {'TIME_WINDOW': (0, RUN_DATA.archive.last_time)}
