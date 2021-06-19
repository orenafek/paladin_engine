"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""
import inspect
import pickle
import sys
import traceback
from types import CodeType

from PaladinEngine.finders import *
from PaladinEngine.module_transformer.module_transformator import ModuleTransformer
from PaladinEngine.stubbers import *
# DO NOT REMOVE!!!!
# noinspection PyUnresolvedReferences
from PaladinEngine.stubs import __FLI__, __AS__, __POST_CONDITION__, archive, __FCS__, __AS__, __AS_FC__
from source_provider import SourceProvider


class PaLaDiNEngine(object):
    ...


# noinspection PyRedeclaration
class PaLaDiNEngine(object):
    """
        Paladin's conversion engine.
    """

    __INSTANCE = PaLaDiNEngine()

    # List of stubs that can be added to the PaLaDiNized code
    __PALADIN_STUBS_LIST = [__FLI__, __POST_CONDITION__, __AS_FC__, __AS__]

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
    def execute_with_paladin(source_code, original_file_name: str):
        """
            Execute a source code with the paladin environment.
        :param source_code:
        :return:
        """
        print(source_code)
        # Set the variables for the run.
        variables = {f.__name__: f for f in PaLaDiNEngine.__PALADIN_STUBS_LIST}

        # Make sure that the script runs as if was alone.
        variables['__name__'] = '__main__'
        variables['__PALADIN_file__'] = original_file_name

        # Collect imports.
        variables.update(PaLaDiNEngine.__collect_imports_to_execution())

        # Set program name.
        sys.argv[0] = original_file_name
        # Clear args.
        sys.argv[1:] = []
        return exec(source_code, variables)

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
            t = t.transform_loop_invariants()
            m = t.module
            t = t.transform_assignments()
            m = t.module
            t = t.transform_function_calls()
            m = t.module
            t = t.transform_for_loops_to_while_loops()
            m = t.module
            t = t.transform_paladin_post_condition()
            m = t.module

        except BaseException as e:
            print(ast2str(m))
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
