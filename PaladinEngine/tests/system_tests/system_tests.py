import os
import threading
import traceback

import pytest
from pycallgraph import PyCallGraph, GlobbingFilter, Config
from pycallgraph.output import GraphvizOutput
from engine.engine import PaLaDiNEngine
from stubs.stubs import archive, __STUBS__


class CallGraphCreator:
    def __init__(self):
        graphviz = GraphvizOutput()
        graphviz.output_file = 'output.png'
        if os.path.exists(graphviz.output_file):
            os.remove(graphviz.output_file)
        trace_filter = GlobbingFilter(
            exclude=[
                'pycallgraph.*'
                'threading.*',
                'argparse.*',
                'pytest.*',
                'Paladin*',
                'engine*',
                'ast*',
                'traceback*',
                'codecs*',
                'linecache*',
                'posixpath*',

            ]

        )

        self.graphviz = graphviz
        config = Config()
        config.trace_filter = trace_filter
        self.config = config


class TestEngine:
    TEST_RESOURCES_RELATIVE_DIR = '../test_resources'
    CALL_GRAPH_CREATOR = CallGraphCreator()

    @staticmethod
    def create_test_source_absolute_path(test_src_name: str):
        return os.path.join(TestEngine.TEST_RESOURCES_RELATIVE_DIR, test_src_name)

    @staticmethod
    def basic_test(test_file_path: str, verbose: bool = False, with_call_graph: bool = False,
                   valid_exceptions: list = []):
        if with_call_graph:
            with PyCallGraph(output=TestEngine.CALL_GRAPH_CREATOR.graphviz,
                             config=TestEngine.CALL_GRAPH_CREATOR.config):
                TestEngine._basic_test(test_file_path, verbose, valid_exceptions)

        else:
            TestEngine._basic_test(test_file_path, verbose, valid_exceptions)

    @staticmethod
    def _basic_test(test_file_path: str, verbose: bool, valid_exceptions: list):
        try:
            engine = PaLaDiNEngine(test_file_path)

            # Reset the archive.
            archive.reset()

            # Execute it.
            engine.execute_with_paladin()

        except BaseException as e:
            traceback.print_exc()
            if type(e) not in valid_exceptions:
                raise e

        finally:
            if verbose:
                # Print the archive.
                # print(archive)
                with open(test_file_path.removesuffix('.py') + '.csv', 'w+') as f:
                    import csv
                    writer = csv.writer(f)
                    header, rows = archive.to_table()
                    writer.writerow(header)
                    writer.writerows(rows)

    # @pytest.mark.skip(reason="")
    def test_0(self):
        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
            r'test_module.py'
        ),
            verbose=True,
            valid_exceptions=[AssertionError]
        )

    @pytest.mark.skip(reason="")
    def test_custom_range(self):
        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
            r'test_module_with_custom_range.py'
        ),
            verbose=True,
            valid_exceptions=[AssertionError]
        )

    @pytest.mark.skip(reason="")
    def test_function_call_stub(self):
        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
            r'test_function_call_store.py'
        ),
            verbose=True,
            valid_exceptions=[AssertionError]
        )

    @pytest.mark.skip(reason="")
    def test_1(self):

        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(r'basic2.py'), verbose=True)

    @pytest.mark.skip(reason="")
    def test_tetris(self):
        class TestThread(threading.Thread):
            def run(self) -> None:
                TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
                    r'../test_resources/Tetris/tetris.py'),
                    verbose=True,
                    with_call_graph=False)

        # class KeyboardThread(threading.Thread):
        #     def run(self) -> None:
        #         from appscript import app
        #         import time
        #         while True:
        #             app('System Events').keystroke(f'{Key.down}')
        #             time.sleep(1)
        #
        # KeyboardThread().start()
        TestThread().run()

    @pytest.mark.skip(reason="")
    def test_lib1_syntax(self):
        TestEngine.basic_test(
            '/tests/test_resources/examples/lab1/src/lambda_calc'
            '/syntax.py', verbose=True)

    # @pytest.mark.skip(reason="")
    def test_lib1_semantics(self):
        TestEngine.basic_test(
            '/tests/test_resources/examples/lab1/src/lambda_calc'
            '/semantics.py', verbose=True)

    # @pytest.mark.skip(reason="")
    def test_2(self):
        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
            r'basic2.py'
        ),
            verbose=True,
            valid_exceptions=[AssertionError]
        )
