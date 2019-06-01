"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""
import traceback
from types import CodeType

import astor

from finders import *
from module_transformer.module_transformator import ModuleTransformer
from stubbers import *
# DO NOT REMOVE!!!!
# noinspection PyUnresolvedReferences
from stubs import __FLI__, __AS__
from stubs import archive


class PaLaDiNEngine(object):
    ...


# noinspection PyRedeclaration
class PaLaDiNEngine(object):
    """
        Paladin's conversion engine.
    """

    __INSTANCE = PaLaDiNEngine()

    __PALADIN_STUBS_LIST = [__AS__, __FLI__]

    __COMPILATION_MODE = 'exec'

    def __new__(cls, *args, **kwargs):
        return PaLaDiNEngine.__INSTANCE

    @staticmethod
    def compile(source_code) -> CodeType:
        # Compile it.
        return compile(source_code, PALADIN_ERROR_FILE_PATH, mode=PaLaDiNEngine.__COMPILATION_MODE)

    @staticmethod
    def execute_with_paladin(source_code):
        """
            Execute a source code with the paladin environment.
        :param source_code:
        :return:
        """
        return exec(source_code,
                    {f.__name__: f for f in PaLaDiNEngine.__PALADIN_STUBS_LIST})

    @staticmethod
    def process_module(module: ast.AST) -> ast.AST:
        """
            Activate all the transformers on a module.
        :param module:
        :return:
        """
        return ModuleTransformer(module) \
            .transform_loop_invariants() \
            .transform_assignments() \
            .module()

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
        return astor.to_source(PaLaDiNEngine.process_module(PaLaDiNEngine.create_module(code)))


def main():
    # Read source file.
    with open(r'tests\test_resources\test_module.py') as f:
        # Read the source file.
        tetris_source_file = f.read()

        # Transform into a PaLaDiN form.
        paladinized = PaLaDiNEngine.transform(tetris_source_file)

        # Print the code.
        print(str(paladinized))

        # Compile it.
        complied_code = PaLaDiNEngine.compile(paladinized)

        try:
            # Execute the code.
            PaLaDiNEngine.execute_with_paladin(complied_code)

        except BaseException:
            traceback.print_exc()

        finally:
            # Print the archive.
            print(archive)


if __name__ == '__main__':
    main()
