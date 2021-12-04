import json
import os
import typing

import networkx as nx
from flask import Flask, render_template, request, jsonify
from flask_classful import FlaskView, route
from flask_cors import CORS

import archive.archive
from PaladinEngine.stubs.stubs import __DEF__, __FC__, __UNDEF__, __AS__, __ARG__, __AC__, __PIS__

NAME = 'PaLaDiN Research Server'
TEMPLATE_FOLDER = os.path.join(os.getcwd(), 'interactive_graph', 'templates')
JSON_FILE_NAME = 'input_graph_tree.json'
SOURCE_CODE: str = ''


class InteractiveGraph(object):
    EDGE_ID_SRC_DEST_SEP = '->'
    EDGE_ID_FORMAT = '{source}' + EDGE_ID_SRC_DEST_SEP + '{target}'
    NODE_COLORS = {
        __DEF__.__name__: 'brown',
        __FC__.__name__: 'blue',
        __AS__.__name__: 'yellow',
        __ARG__.__name__: 'red',
        __AC__.__name__: 'pink',
        __PIS__.__name__: 'cyan'
    }

    def __init__(self, _a: archive.archive.Archive):
        self.archive = _a
        # self._app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
        #                      name=InteractiveGraph.__name__)
        # self._app.layout = self._app_layout
        self._nodes_state = {}

    @property
    def _archive_as_graph(self):

        def repr_node(rv: archive.archive.Archive.Record.RecordValue):
            if rv.key.stub_name == __ARG__.__name__ or rv.key.stub_name == __AS__.__name__:
                node_expr = f'{rv.expression}={rv.value}'
            else:
                node_expr = rv.expression

            return \
                rv.key.stub_name.strip('__'), \
                node_expr, \
                f'{rv.time}', \
                rv.key.stub_name, \
                str(rv.time), \
                str(rv.key.container_id), \
                str(rv.key.field), \
                str(archive.archive.represent(rv.value)), \
                str(rv.line_no)

        def add_node_to_graph(rv, color='white'):
            g.add_node(repr_node(rv), fillcolor=color, color=color)

        def add_edge_to_graph(from_rv, to_rv):
            g.add_edge(repr_node(from_rv), repr_node(to_rv))

        def add_children(node, record_values: typing.List[archive.archive.Archive.Record.RecordValue]) -> typing.List[
            archive.archive.Archive.Record.RecordValue]:

            next_def_node = None

            while record_values:
                next_node = record_values[0]

                node_type = next_node.key.stub_name
                if node_type == __DEF__.__name__:
                    if not next_def_node:
                        # TODO: This is for function calls that are not PaLaDiNized,
                        #       meaning, there is no __FC__ before __DEF__
                        next_def_node = node if node.key.stub_name == __FC__.__name__ else next_node
                    record_values = add_children(next_def_node, record_values[1::])
                    continue
                if node_type == __UNDEF__.__name__:
                    return record_values[1::]

                if node_type == __FC__.__name__:
                    color = 'blue'
                    next_def_node = next_node

                elif node_type == __AS__.__name__:
                    color = 'red'

                elif node_type == __ARG__.__name__:
                    color = 'green'

                elif node_type == __AC__.__name__:
                    color = 'pink'
                else:
                    color = 'yellow'

                add_node_to_graph(next_node, color)
                add_edge_to_graph(node, next_node)
                if not record_values:
                    return

                record_values = record_values[1::]

        # Create a graph.
        g = nx.DiGraph()

        all_record_values = self.archive.record_values_sorted_by_time

        # Get the first node.
        try:
            first_node = [rv for rv in all_record_values if rv.key.stub_name == __FC__.__name__][0]
        except IndexError:
            return None

        add_node_to_graph(first_node, color='blue')
        record_values = all_record_values[all_record_values.index(first_node) + 1::]
        record_values = add_children(first_node, record_values)
        while record_values:
            if record_values[0].key.stub_name == __UNDEF__.__name__ and \
                    record_values[0].key.field == first_node.key.field:
                break
            record_values = add_children(first_node, record_values)

        return g

    @property
    def archive_as_json_graph(self):
        g = self._archive_as_graph
        if not g:
            return '{}'
        roots = [n for n in g.nodes if g.in_degree(n) == 0]
        r = roots[0]

        def generate_dict(n, p_name):
            d = {
                "parent": p_name,
                "name": n[0],
                "expression": n[1],
                "time": n[2],
                "stub_name": n[3],
                "container": n[5],
                "field": n[6],
                "value": n[7],
                "line_no": n[8],
                "color": InteractiveGraph.NODE_COLORS[n[3]],
                "children": []
            }

            if not g.successors(n):
                return d

            d["children"] = [
                generate_dict(child, n[0]) for child in g.successors(n)
            ]

            return d

        return json.dumps(generate_dict(r, "null"))

    def run_collapsible_tree(self, source_code: str, port: int = 9999) -> None:
        global SOURCE_CODE, IG
        server = PaladinFlaskServer()
        self.dump_graph_to_json(file_name=JSON_FILE_NAME)
        SOURCE_CODE = source_code
        IG = self
        server.register_app()
        server.run(port)

    def dump_graph_to_json(self, file_name: str):
        with open(os.path.join(TEMPLATE_FOLDER, file_name), 'w') as f:
            f.write(self.archive_as_json_graph)

    def search(self, expr: str):
        return self.archive.search_web(expr)


IG: typing.Optional[InteractiveGraph] = None


class PaladinFlaskServer(FlaskView):

    def __init__(self):
        self._app = Flask(NAME, template_folder=TEMPLATE_FOLDER)
        CORS(self.app, resources={r'/*': {'origins': '*'}})

    def register_app(self):
        self.app.template_folder = TEMPLATE_FOLDER
        PaladinFlaskServer.register(self.app, route_base='/')

    @property
    def app(self):
        return self._app

    @route('/', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'GET':
            return render_template('index.html')
        if request.method == 'POST':
            return self.search()

    @route('/input_graph_tree.json')
    def input_graph_tree(self):
        with open(os.path.join(TEMPLATE_FOLDER, JSON_FILE_NAME), 'r') as f:
            return f.read()

    @route('/source_code.txt')
    def src_code(self):
        return SOURCE_CODE

    @route('/search', methods=['POST'])
    def search(self):
        if not request.json:
            result = {'search_result': ''}
        else:
            result = {'search_result': IG.search(request.json['expression_to_search'])}
        return result

    def run(self, port: int = 5000):
        self.app.run(port=port)
