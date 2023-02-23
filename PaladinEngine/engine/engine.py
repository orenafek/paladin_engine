"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""
import ast
import dataclasses
import inspect
import pickle
import re
import signal
import sys
import traceback
from contextlib import redirect_stdout
from io import StringIO
from types import CodeType
from typing import Tuple, Any, Optional

from archive.archive import Archive
from ast_common.ast_common import ast2str
from conf.engine_conf import PALADIN_ERROR_FILE_PATH
from module_transformer.module_transformator import ModuleTransformer
from source_provider.source_provider import SourceProvider
# DO NOT REMOVE!!!!
# noinspection PyUnresolvedReferences
from stubs.stubs import __FLI__, __AS__, __POST_CONDITION__, archive, __AS__, __FC__, __FRAME__, __ARG__, \
    __DEF__, __UNDEF__, __AC__, __PIS__, __PALADIN_LIST__, __IS_STUBBED__, __BREAK__, __EOLI__, __SOLI__, __BMFCS__, \
    __PRINT__


class PaLaDiNEngine(object):
    ...


# noinspection PyRedeclaration
class PaLaDiNEngine(object):
    """
        Paladin's conversion engine.
    """

    @dataclasses.dataclass
    class PaladinRunExceptionData(object):
        """
            Data for an exception the occures during a PaLaDiNized run of a code.
        """
        source_code_line_no: int
        paladinized_code_line_no: int
        exception_msg: str
        source_line: str
        archive_time: int

        @staticmethod
        def create(source_code: str, paladinized_code: str, sys_exc_info,
                   archive_time: int, exception_line_no: int = -1) -> 'PaLaDiNEngine.PaladinRunExceptionData':

            if exception_line_no == -1:
                run_line_no = None
                exc_info: traceback = sys_exc_info[2]
                while exc_info:
                    run_line_no = exc_info.tb_lineno
                    exc_info = exc_info.tb_next
            else:
                run_line_no = exception_line_no

            original_lines = source_code.split('\n')
            paladinized_lines = paladinized_code.split('\n')

            paladinized_line = paladinized_lines[run_line_no - 1]

            if __IS_STUBBED__(paladinized_line):
                # The line itself is not as it was in the original file, therefore look for the line no. in it.
                try:
                    line_no = int(
                        re.compile(r'.*line_no=(?P<lineno>[0-9]+).*').match(paladinized_line).groupdict()['lineno'])
                except BaseException as e:
                    if __FC__.__name__ in paladinized_line:
                        # TODO: This is a patch for __FC__ that can't add "line_no=" in it because it expects *args and **kwargs after it.
                        # TODO: Currently assuming that __FC__(expression, func_name, locals, globals, frame, line_no, *args, **kwargs)
                        start_of_line_no = paladinized_line.index(f'{__FRAME__.__name__}(), ') + len(f'{__FRAME__.__name__}(), ')
                        line_no = int(re.compile(r'(?P<n>(\d+))[,)].*').match(paladinized_line[start_of_line_no::]).group('n'))
                        #line_no = int(paladinized_line.split(',')[5].strip().strip(')'))
                    else:
                        raise e

                matched_line = (line_no, original_lines[line_no - 1])  # original_lines start from 0
            else:
                matched_lines = [(no + 1, l) for no, l in enumerate(original_lines) if
                                 paladinized_lines[run_line_no - 1] == l]
                # TODO: What to do if there are more (or less) than 1?
                assert len(matched_lines) == 1

                matched_line = matched_lines[0]
            return PaLaDiNEngine.PaladinRunExceptionData(source_code_line_no=matched_line[0],
                                                         paladinized_code_line_no=run_line_no - 1,
                                                         exception_msg=str(sys_exc_info[1]),
                                                         source_line=matched_line[1],
                                                         archive_time=archive_time)

    __INSTANCE = PaLaDiNEngine()

    # List of stubs that can be added to the PaLaDiNized code
    PALADIN_STUBS_LIST = [__FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__, __ARG__, __DEF__, __UNDEF__, __AC__,
                          __PIS__, __PALADIN_LIST__, __BREAK__, __SOLI__, __EOLI__, __BMFCS__, __PRINT__]

    # Mode of Pythonic compilation.
    __COMPILATION_MODE = 'exec'

    __SOURCE_PROVIDER = None

    @staticmethod
    def get_source_provider():
        return PaLaDiNEngine.__SOURCE_PROVIDER

    def __new__(cls, *args, **kwargs):
        """
        Constructor for PaLaDiNEngine class.
        Keeps the engine singleton.
        :param args:
        :param kwargs:
        """
        return PaLaDiNEngine.__INSTANCE

    @staticmethod
    def compile(source_code) -> CodeType:
        # Compile it.
        return compile(source_code, PALADIN_ERROR_FILE_PATH, mode=PaLaDiNEngine.__COMPILATION_MODE)

    @staticmethod
    def execute_with_paladin(source_code: str, paladinized_code: str, original_file_name: str, timeout: int = -1,
                             output_capture: StringIO = None) -> Tuple[Any, Archive, Optional[PaladinRunExceptionData]]:
        """
            Execute a source code with the paladin environment.
        :param source_code:
        :param paladinized_code:
        :param original_file_name
        :param timeout
        :param output_capture
        :return:
        """
        # Set the variables for the run.
        variables = {f.__name__: f for f in PaLaDiNEngine.PALADIN_STUBS_LIST}

        # Make sure that the script runs as if was alone.
        variables['__name__'] = '__main__'
        variables['__PALADIN_file__'] = original_file_name

        # Collect imports.
        variables.update(PaLaDiNEngine.__collect_imports_to_execution())

        # Set program name.
        sys.argv[0] = original_file_name
        # Clear args.
        sys.argv[1:] = []

        class PaladinTimeoutError(TimeoutError):
            def __init__(self, line_no: int, *args, **kwargs):
                super(PaladinTimeoutError, self).__init__(args, kwargs)
                self.line_no = line_no

        try:
            def handler(signum, frame):
                current_frame = frame
                while current_frame and 'PALADIN' not in str(current_frame):
                    current_frame = current_frame.f_back

                raise PaladinTimeoutError(current_frame.f_lineno,
                                          f'Program exceeded timeout, stopped on: {current_frame.f_lineno}')

            signal.signal(signal.SIGALRM, handler)

            if timeout > 0:
                signal.alarm(timeout)

            if output_capture is not None:
                with redirect_stdout(output_capture):
                    return exec(compile(paladinized_code, 'PALADIN', 'exec'), variables), archive, None

            return exec(compile(paladinized_code, 'PALADIN', 'exec'), variables), archive, None

        except (PaladinTimeoutError, BaseException) as e:
            return None, archive, PaLaDiNEngine.PaladinRunExceptionData \
                .create(source_code, paladinized_code,
                        sys.exc_info(),
                        archive.time,
                        e.line_no if isinstance(e, PaladinTimeoutError) else -1)

    @staticmethod
    def __collect_imports_to_execution():
        return {module.__name__: module for module in [sys, inspect]}

    @staticmethod
    def process_module(module: ast.AST) -> ast.AST:
        """
            Activate all the transformers on a module.
        :param module:
        :return:
        """

        t = ModuleTransformer(module)
        m = module
        try:
            t = t.transform_aug_assigns()
            m = t.module
            t = t.transform_loop_invariants()
            m = t.module
            t = t.transform_function_calls()
            m = t.module
            # t = t.transform_attribute_accesses()
            # m = t.module
            t = t.transform_loops()
            m = t.module
            t = t.transform_assignments()
            m = t.module
            t = t.transform_function_def()
            m = t.module
            t = t.transform_paladin_post_condition()
            m = t.module
            t = t.transform_breaks()
            m = t.module

        except BaseException as e:
            print(e)
        return t.module

    @staticmethod
    def create_module(src_file) -> ast.AST:
        """
            Create an AST object out of a string of a source file.
        :param src_file: (str) Source code.
        :return: (Node) An AST node.
        """
        return ast.parse(src_file)

    @staticmethod
    def transform(code: str) -> str:
        """
            Transform a code into a code with PaLaDiN.
        :param code: (str) source code.
        :return: (str) The PaLaDiNized code.
        """
        SourceProvider.set_code(code)
        return ast2str(
            PaLaDiNEngine.process_module(
                PaLaDiNEngine.create_module(code)))

    @staticmethod
    def transform_and_pickle(code: str) -> bytes:
        return pickle.dumps(PaLaDiNEngine.process_module(PaLaDiNEngine.create_module(code)))

    @staticmethod
    def import_line(import_path):
        return f'from {import_path} import {", ".join([stub.__name__ for stub in PaLaDiNEngine.PALADIN_STUBS_LIST])}'


def main():
    # Read source file.
    file_name = r'tests/test_resources/test_module.py'
    with open(file_name) as f:
        # Read the source file.
        tetris_source_file = f.read()

        # Transform into a PaLaDiN form.
        paladinized = PaLaDiNEngine.transform(tetris_source_file)

        # Print the code.
        print(str(paladinized))

        # Compile it.
        try:
            complied_code = PaLaDiNEngine.compile(paladinized)

            # Execute the code.
            PaLaDiNEngine.execute_with_paladin(complied_code, file_name)

        except BaseException:
            traceback.print_exc()

        finally:
            # Print the archive.
            print(archive)


if __name__ == '__main__':
    main()
