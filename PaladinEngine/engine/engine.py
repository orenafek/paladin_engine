"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""
import ast
import inspect
import pickle
import re
import signal
import sys
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass, asdict
from io import StringIO
from pathlib import Path
from time import time
from types import CodeType
from typing import Optional, Union, Tuple

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time
from ast_common.ast_common import ast2str, get_arg_from_func_call
from conf.engine_conf import PALADIN_ERROR_FILE_PATH
from module_transformer.global_map import GlobalMap
from module_transformer.module_transformator import ModuleTransformer
# DO NOT REMOVE!!!!
# noinspection PyUnresolvedReferences
from stubs.stubs import __FLI__, __POST_CONDITION__, archive, __AS__, __FC__, __FRAME__, __ARG__, \
    __DEF__, __UNDEF__, __AC__, __PIS__, __PALADIN_LIST__, __IS_STUBBED__, __BREAK__, __EOLI__, __SOLI__, __BMFCS__, \
    __PRINT__, __STUBS__
# noinspection PyUnresolvedReferences
from api.api import PaladinPostCondition


# noinspection PyRedeclaration
class PaLaDiNEngine(object):
    """
        Paladin's conversion engine.
    """

    @dataclass
    class PaladinRunExceptionData(object):
        """
            Data for an exception the occures during a PaLaDiNized run of a code.
        """
        line_no: int
        paladinized_line_no: int
        msg: str
        throwing_line_source: str
        time: Time

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
                    for stub in {__FC__, __PRINT__}:
                        if line_no := get_arg_from_func_call(paladinized_line, stub, 'line_no'):
                            break
                    else:
                        raise e
                line_no = int(line_no)
                matched_line = (line_no, original_lines[line_no - 1])  # original_lines start from 0
            else:
                matched_lines = [(no + 1, l) for no, l in enumerate(original_lines) if
                                 paladinized_lines[run_line_no - 1] == l]
                # TODO: What to do if there are more (or less) than 1?
                # assert len(matched_lines) == 1

                matched_line = matched_lines[0]
            return PaLaDiNEngine.PaladinRunExceptionData(line_no=matched_line[0],
                                                         paladinized_line_no=run_line_no - 1,
                                                         msg=str(sys_exc_info[1]),
                                                         throwing_line_source=matched_line[1],
                                                         time=archive_time)

        @classmethod
        def empty(cls):
            return PaLaDiNEngine.PaladinRunExceptionData(-1, -1, '', '', -1)

        @property
        def as_dict(self):
            return asdict(self)

    @dataclass
    class PaladinRunData(object):
        output: str
        archive: Archive
        thrown_exception: Optional['PaLaDiNEngine.PaladinRunExceptionData']

    def __init__(self, source_path: Union[str, Path], timeout: int = -1, record: bool = True):
        self.source_path: Path = source_path if isinstance(source_path, Path) else Path(source_path)
        self.file_name: str = self.source_path.name
        self.timeout: int = timeout
        self.output_capture: Optional[StringIO] = StringIO() if record else None
        with open(source_path, 'r') as f:
            self.source_code: str = f.read()

        self._paladinized_code, self._global_map, self.transformation_time = self.transform(self.source_code)

        self._run_data: Optional['PaLaDiNEngine.PaladinRunData'] = None

    # Mode of Pythonic compilation.
    __COMPILATION_MODE = 'exec'

    __SOURCE_PROVIDER = None

    @property
    def paladinized_code(self):
        return self._paladinized_code

    @paladinized_code.setter
    def paladinized_code(self, value: str):
        self._paladinized_code = value

    @property
    def global_map(self):
        return self._global_map

    @global_map.setter
    def global_map(self, value):
        self._global_map = value

    @property
    def run_data(self) -> Optional['PaLaDiNEngine.PaladinRunData']:
        return self._run_data

    @property
    def source_provider(self):
        return PaLaDiNEngine.__SOURCE_PROVIDER

    def write_paladinized(self, output_path: Path):
        with open(output_path, 'w+') as fo:
            fo.write(PaLaDiNEngine.import_line('stubs.stubs'))
            fo.writelines('\n' * 3)
            fo.write(self.paladinized_code)

    def compile(self) -> CodeType:
        # Compile it.
        return compile(self.source_code, PALADIN_ERROR_FILE_PATH, mode=PaLaDiNEngine.__COMPILATION_MODE)

    def execute_with_paladin(self):
        """
            Execute a source code with the paladin environment.
        :param output_capture
        :return:
        """
        # Set the variables for the run.
        variables = {f.__name__: f for f in __STUBS__}

        # Make sure that the script runs as if was alone.
        variables['__name__'] = '__main__'
        variables['__PALADIN_file__'] = self.file_name

        # Collect imports.
        variables.update(PaLaDiNEngine.__collect_imports_to_execution())

        # Set program name.
        sys.argv[0] = self.file_name
        # Clear args.
        sys.argv[1:] = []

        class PaladinTimeoutError(TimeoutError):
            def __init__(self, line_no: int, *args, **kwargs):
                super(PaladinTimeoutError, self).__init__(args, kwargs)
                self.line_no = line_no

        thrown_exception: Optional[PaLaDiNEngine.PaladinRunExceptionData] = None
        output: Optional[str] = None
        try:
            def handler(signum, frame):
                current_frame = frame
                line_no = frame.f_lineno
                while current_frame and 'PALADIN' not in str(current_frame):
                    line_no = current_frame.f_lineno
                    current_frame = current_frame.f_back
                raise PaladinTimeoutError(line_no,
                                          f'Program exceeded timeout, stopped on: {line_no}')

            if self.timeout > 0:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(self.timeout)

            archive.reset()

            if self.output_capture is not None:
                self.output_capture = StringIO()
                with redirect_stdout(self.output_capture):
                    exec(compile(self.paladinized_code, 'PALADIN', 'exec'), variables)
                    output = self.output_capture.getvalue()
            else:
                exec(compile(self.paladinized_code, 'PALADIN', 'exec'), variables)

        except (PaladinTimeoutError, BaseException) as e:
            thrown_exception = PaLaDiNEngine.PaladinRunExceptionData \
                .create(self.source_code, self.paladinized_code,
                        sys.exc_info(),
                        archive.time,
                        e.line_no if isinstance(e, PaladinTimeoutError) else -1)

        self._run_data = PaLaDiNEngine.PaladinRunData(output, archive, thrown_exception)

    def update_source_code(self, updated_source_code: str):
        with open(self.source_path, 'w') as f:
            f.write(updated_source_code)

        self.source_code = updated_source_code
        self.paladinized_code, self.global_map, _ = self.transform(self.source_code, False)

    @staticmethod
    def __collect_imports_to_execution():
        return {module.__name__: module for module in [sys, inspect]}

    @staticmethod
    def process_module(module: ast.AST) -> Tuple[ast.AST, GlobalMap]:
        """
            Activate all the transformers on a module.
        :param module:
        :return:
        """

        t = ModuleTransformer(module)
        try:
            t.transform_aug_assigns() \
                .transform_function_calls() \
                .transform_loops() \
                .transform_assignments() \
                .transform_function_def() \
                .transform_breaks()

        except BaseException as e:
            print(e)
        return t.module, t.global_map

    @staticmethod
    def create_module(src_file) -> ast.AST:
        """
            Create an AST object out of a string of a source file.
        :param src_file: (str) Source code.
        :return: (Node) An AST node.
        """
        return ast.parse(src_file)

    def transform(self, code: str, should_time_transformation: bool = True) -> Tuple[str, GlobalMap, Optional[float]]:
        """
            Transform a code into a code with PaLaDiN.
        :param code: (str) source code.
        :param should_time_transformation: (bool) Should measure time of transformation
        :return: (str) The PaLaDiNized code.
        """
        start_time = time()
        paladinized_module, global_map = PaLaDiNEngine.process_module(PaLaDiNEngine.create_module(code))
        end_time = time()
        return ast2str(paladinized_module), global_map, end_time - start_time if should_time_transformation else None

    @staticmethod
    def transform_and_pickle(code: str) -> bytes:
        return pickle.dumps(PaLaDiNEngine.process_module(PaLaDiNEngine.create_module(code)))

    @staticmethod
    def import_line(import_path):
        return f'from {import_path} import {", ".join([stub.__name__ for stub in __STUBS__])}'
