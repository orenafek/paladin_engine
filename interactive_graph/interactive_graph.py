import http.server
import json
import os
import random
import shutil
import socketserver
import typing

import dash_cytoscape as cyto
import dash_html_components as html
import networkx as nx
from dash_extensions.enrich import Output, Input
from networkx.drawing.nx_agraph import to_agraph

import archive.archive
from PaladinEngine.stubs.stubs import __DEF__, __FC__, __UNDEF__, __AS__, __ARG__


class InteractiveGraph(object):
    EDGE_ID_SRC_DEST_SEP = '->'
    EDGE_ID_FORMAT = '{source}' + EDGE_ID_SRC_DEST_SEP + '{target}'
    NODE_COLORS = {
        __DEF__.__name__: 'blue',
        __FC__.__name__: 'red',
        __AS__.__name__: 'yellow',
        __ARG__.__name__: 'brown',
    }

    class GraphIterator(object):
        def __init__(self, ig):
            self.ig = ig
            self.graph: nx.DiGraph = ig._archive_as_graph

        def create_sub_graph(self, nodes) -> tuple[list[dict], list[dict]]:
            if not isinstance(nodes, list):
                nodes = [nodes]

            # Accumulate successors for nodes.
            successors = []
            for n in nodes:
                successors.extend(self.graph.successors(n))

            subgraph: nx.Graph = self.graph.subgraph(nodes + successors)
            graph_nodes = self.ig._graph_nodes(subgraph.nodes)
            graph_edges = self.ig._graph_edges(subgraph.edges)

            return graph_nodes, graph_edges

        def create_complement_graph_with_node(self, graph: nx.DiGraph, node):
            def _spanned_nodes(node):
                spanned = []
                for s in graph.successors(node):
                    spanned.extend(_spanned_nodes(s))
                    spanned.append(s)

                return spanned

            # Get all spanned nodes from node.
            node_subgraph = graph.subgraph(_spanned_nodes(node))

            # Subtract the graphs.
            complement_graph = graph.copy()
            complement_graph.remove_edges_from(node_subgraph.edges)
            complement_graph.remove_nodes_from(node_subgraph.nodes)

            graph_nodes = self.ig._graph_nodes(complement_graph.nodes)
            graph_edges = self.ig._graph_edges(complement_graph.edges)

            return graph_nodes, graph_edges

    def __init__(self, _a: archive.archive.Archive):
        self.archive = _a
        # self._app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
        #                      name=InteractiveGraph.__name__)
        # self._app.layout = self._app_layout
        self._nodes_state = {}

    def _graph_nodes(self, nodes=None):

        label_maker = lambda node: f'{node[0] if len(node[0]) <= 10 else node[0][:10] + "..."}:{node[2]}'
        return \
            [
                {
                    'data': {'id': node[0], 'label': label_maker(node), 'type': node[1], 'time': node[2],
                             'container_id': node[3]},
                    'position': {'x': 40 * i, 'y': 60 * i},
                    'size': 30,
                    'style': {'background-color': InteractiveGraph.NODE_COLORS[node[1]]}
                }
                for i, node in enumerate(nodes if nodes else self._archive_as_graph.nodes)
            ]

    @property
    def _archive_as_graph(self):

        def repr_node(rv: archive.archive.Archive.Record.RecordValue):
            if rv.key.stub_name == __ARG__.__name__ or rv.key.stub_name == __AS__.__name__:
                node_expr = f'{rv.expression}={rv.value}'
            else:
                node_expr = rv.expression

            return \
                node_expr \
                    if len(node_expr) <= 10 \
                    else node_expr[0:10] + '...' + f' ({rv.time})', \
                node_expr, \
                f'{rv.time}', \
                rv.key.stub_name, \
                str(rv.time), \
                str(rv.key.container_id), \
                str(rv.value), \
                str(rv.line_no)

        def add_node_to_graph(rv, color='white'):
            g.add_node(repr_node(rv), fillcolor=color, color=color)

        def add_edge_to_graph(from_rv, to_rv):
            g.add_edge(repr_node(from_rv), repr_node(to_rv))

        def add_children(node, record_values: typing.List[archive.archive.Archive.Record.RecordValue]) -> typing.List[
            archive.archive.Archive.Record.RecordValue]:

            while record_values:

                next_node = record_values[0]

                node_type = next_node.key.stub_name
                if node_type == __DEF__.__name__:
                    record_values = add_children(next_node, record_values[1::])

                if node_type == __UNDEF__.__name__:
                    return record_values[1::]

                if node_type == __FC__.__name__:
                    color = 'blue'

                elif node_type == __AS__.__name__:
                    color = 'red'

                elif node_type == __ARG__.__name__:
                    color = 'green'
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
            first_node = [rv for rv in all_record_values if rv.key.stub_name == __DEF__.__name__][0]
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
    def _nodes(self):
        return [(rk, rv) for (rk, rv) in self.archive.records.items() if rk.stub_name == __DEF__.__name__]

    def _get_callees(self, record: archive.archive.Archive.Record.RecordValue) -> list:
        sorted_archive = self.archive.flat_and_sort_by_time()
        next_func_in_archive = [rv for rk, rv in sorted_archive if
                                rv.time + 1 == record[0].time]  # TODO: Replace record[0]
        if not next_func_in_archive:
            return [rv for rk, rv in sorted_archive if rk.stub_name == __FC__.__name__]
        else:
            return [rv for rk, rv in sorted_archive if
                    rk.stub_name == __FC__.__name__ and rv.time < next_func_in_archive[0].time]

    @property
    def _edges(self):
        return [(rv[0], callee) for _, rv in self._nodes for callee in self._get_callees(rv)]

    def _graph_edges(self, edges=None):
        if edges is not None and list(edges) == []:
            return []
        return [
            {
                'data': {'source': source[0], 'target': target[0],
                         'id': InteractiveGraph.EDGE_ID_FORMAT.format(source=source[0], target=target[0])},
                'style': {'target-arrow-shape': 'triangle'}
            }
            for source, target in (edges if edges else self._archive_as_graph.edges)]
        # return [{'data': {'source': source.key.field, 'target': target.key.field}} for source, target in self._edges
        #         # FIXME: Patch because constructors' __DEF__ stub doesn't match their call:
        #         # FIXME: class X():
        #         # FIXME:     def __init__(self, ...):
        #         # FIXME:         ....
        #         # FIXME: ...
        #         # FIXME: x = X(...)
        #         # FIXME: __FC__('X' , ...) !@!@!@!@ Instead of calling '__init__' we have 'X')
        #         # FIXME: This can be easily fixed by changing __DEF__('__init__') to __DEF__('X')
        #         if source.key.field != 'Vector' and target.key.field != 'Vector']

    @property
    def app(self):
        return self._app

    @property
    def _styles(self):
        return \
            {
                'pre': {
                    'border': 'thin lightgrey solid',
                    'overflowX': 'scroll'
                }
            }

    @property
    def _default_stylesheet(self):
        return [
            {
                'selector': 'node',
                'style': {
                    # 'background-color': 'blue',
                    'label': 'data(label)'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    "curve-style": "bezier",
                    'target-arrow-shape': 'triangle',
                }
            }

        ]

    @staticmethod
    def in_graph(element: dict, graph: list[dict]):
        element_id = element['data']['id']

        # Check if the element is a node or an edge.
        if InteractiveGraph.EDGE_ID_SRC_DEST_SEP in element_id:
            # The element is an edge.
            return any([_ for _ in graph if _['data']['id'] == element_id])

        # The element is a node.
        return any([_ for _ in graph if _['data']['id'] == element_id])

    @property
    def _app_layout(self):
        return html.Div([
            html.Button(id='cytoscape-button-reset', children=['Reset']),
            cyto.Cytoscape(
                id='cytoscape-event-callbacks-1',
                layout={'name': 'breadthfirst', 'directed': True, 'grid': True},
                elements=self._create_init_graph(),
                stylesheet=self._default_stylesheet,
                style={'width': '100%', 'height': '1000px'}
            ),
            html.Pre(id='cytoscape-tapNodeData-json', style=self._styles['pre']),
        ])

    def run(self):
        self.app.run_server(debug=False)

    def print_static_graph(self, static_graph_file_name: str):
        g = self._archive_as_graph
        g.graph['graph'] = {'rankdir': 'TD'}
        g.graph['node'] = {'shape': 'circle'}
        g.graph['edges'] = {'arrowsize': '4.0'}
        nx.draw_networkx(g)
        A = to_agraph(g)
        print(A)
        A.layout('dot')
        A.draw(static_graph_file_name)

    def create_reset_button_callback(self, igi):
        @self.app.callback(Output('cytoscape-event-callbacks-1', 'elements'),
                           Input('cytoscape-button-reset', 'n_clicks'),
                           prevent_initial_call=True)
        def resetRoot(n_clicks: int):
            self._nodes_state.clear()
            return self._create_init_graph()

        return resetRoot

    def create_tap_node_data_callback(self, igi):
        @self.app.callback(Output('cytoscape-event-callbacks-1', 'elements'),
                           Input('cytoscape-event-callbacks-1', 'tapNodeData'),
                           Input('cytoscape-event-callbacks-1', 'elements'),
                           prevent_initial_call=True)
        def displayTapNodeData(data, elements):
            if not data:
                return elements

            # If the type of the node is not __DEF__, leave.
            if data['type'] != __DEF__.__name__:
                return elements

            # If the node have never been tapped, add it to the state dict.
            tapped_node_id = data['id']
            if tapped_node_id not in self._nodes_state:
                self._nodes_state[tapped_node_id] = False

            node = (tapped_node_id, data['type'], data['time'], data['container_id'])

            # Check if the node is open.
            if self._nodes_state[tapped_node_id]:
                # Mark that its collapsed.
                self._nodes_state[tapped_node_id] = False
                # Collapse its subgraph.
                graph_nodes, graph_edges = igi.create_complement_graph_with_node(self._archive_as_graph, node)
                return graph_nodes + graph_edges

            else:
                # Mark that it is open.
                self._nodes_state[tapped_node_id] = True

                # Assemble subgraph, rooted by the selected node.
                graph_nodes, graph_edges = igi.create_sub_graph(node)
                # Open the graph.
                return elements + (graph_nodes + graph_edges)

        return displayTapNodeData

    def _create_init_graph(self):
        # Create graph iterator.
        igi = InteractiveGraph.GraphIterator(self)

        graph: nx.DiGraph = self._archive_as_graph

        # Extract roots.
        graph_roots = [n for n in graph.nodes if graph.in_degree(n) == 0]

        # Create subgraph.
        graph_nodes, graph_edges = igi.create_sub_graph(graph_roots)

        return graph_nodes + graph_edges

    @property
    def archive_as_json_graph(self):
        g = self._archive_as_graph

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
                "value": n[6],
                "line_no": n[7],
                "children": []
            }

            if not g.successors(n):
                return d

            d["children"] = [
                generate_dict(child, n[0]) for child in g.successors(n)
            ]

            return d

        return json.dumps(generate_dict(r, "null"))

    def run_collapsible_tree(self, source_code_file_path: str, port: int=9999) -> None:
        interactive_graph_dir = '/Users/orenafek/Projects/Paladin/PaladinEngine/interactive_graph'
        with open(os.path.join(interactive_graph_dir, 'input_graph_tree.json'), 'w+') as f:
            f.write(self.archive_as_json_graph)
        os.chdir(interactive_graph_dir)
        html_file_name = 'index.html'

        class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = '/' + html_file_name
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

        # Create an object of the above class
        handler_object = MyHttpRequestHandler

        my_server = socketserver.TCPServer(("", port), handler_object)

        # Create the source code file.
        shutil.copyfile(source_code_file_path,
                        os.path.join(interactive_graph_dir, 'source_code.txt'))

        # Star the server
        print(f'Serving on 127.0.0.1:{port}')
        my_server.serve_forever()
