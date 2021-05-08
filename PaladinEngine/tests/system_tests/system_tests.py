import os
import threading
import traceback

import pytest
from pycallgraph import PyCallGraph, GlobbingFilter, Config
from pycallgraph.output import GraphvizOutput

from PaladinEngine.engine.engine import PaLaDiNEngine
from PaladinEngine.stubs import archive


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

        # Read source file.
        with open(test_file_path) as f:
            # Read the source file.
            source_code = f.read()

            # Transform into a PaLaDiN form.
            paladinized_source_code = PaLaDiNEngine.transform(source_code)

            # Print the code.
            if verbose:
                print(str(paladinized_source_code))
                with open(test_file_path.replace('.py', '_output.py'), 'w+') as f:
                    f.write('import sys\n')
                    f.writelines('from PaladinEngine.stubs import __AS__, __FLI__, __FCS__, __POST_CONDITION__\n')
                    f.write(paladinized_source_code)

            # Compile it.
            complied_code = PaLaDiNEngine.compile(paladinized_source_code)

            # Execute the code.
            try:
                PaLaDiNEngine.execute_with_paladin(complied_code, test_file_path)

            except Exception as e:
                traceback.print_exc()
                if type(e) not in valid_exceptions:
                    raise e

            finally:
                if verbose:
                    # Print the archive.
                    print(archive)

    @pytest.mark.skip(reason="")
    def test_0(self):
        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
            r'test_module.py'
        ),
            verbose=True,
            valid_exceptions=[AssertionError]
        )

    @pytest.mark.skip(reason="")
    def test_3(self):
        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(
            r'test_module3.py'
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

        TestEngine.basic_test(TestEngine.create_test_source_absolute_path(r'test_module2.py'), verbose=True)

    @pytest.mark.skip(reason="")
    def test_2(self):
        self.basic_test(self.test_0, with_call_graph=True)

    @pytest.mark.skip(reason="")
    def test3(self):
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

    def testLib1(self):
        TestEngine.basic_test(
            '/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/lab1/src/lambda_calc'
            '/syntax.py', verbose=True)
