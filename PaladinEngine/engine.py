"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""

import astor

from conf.engine_conf import *
from finders import PaladinInlineDefinitionFinder
from stubbers import LoopStubber
from stubs import create_ast_stub, for_loop_stub


def create_ast(src_file) -> ast.AST:
    """
        Create an AST object out of a string of a source file.
    :param src_file: (str) A source file.
    :return: (Node) An AST node.
    """
    return ast.parse(src_file)


def main():
    # Read source file.
    with open(
            r'C:\Users\Owner\Documents\master\Project A\paladin_engine\PaladinEngine\tests\test_resources\test_module'
            r'.py',
            'rb') as f:
        tetris_source_file = f.read()

    parsed_ast = create_ast(tetris_source_file)

    pidf = PaladinInlineDefinitionFinder()
    pidf.visit(parsed_ast)
    loops = pidf.inline_loops()

    # Take the first loop.
    loop = [l for l in loops.keys()][0]

    # Create a stub.
    stub = create_ast_stub(for_loop_stub, loop.target.id)

    # Create a stuber.
    stuber = LoopStubber(parsed_ast, loop)

    # Stub the loop invariant.
    module = stuber.stub_loop_invariant(stub)

    # Convert back to source.
    source_code = astor.to_source(module)

    # Print the source code.
    print(source_code)

    # Print a separator.
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # Run it.
    exec(source_code)


if __name__ == '__main__':
    main()
