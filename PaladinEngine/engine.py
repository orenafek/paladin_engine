"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""

import astor
from astunparse import unparse

from finders import *
from stubbers import *
from stubs import __AS__, __FLI__, create_ast_stub


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

    module = create_ast(tetris_source_file)

    pidf = PaladinInlineDefinitionFinder()
    pidf.visit(module)
    loops = pidf.find()

    # Take the first loop.
    loop = [l for l in loops.keys()][0]

    # Create a stub.
    stub = create_ast_stub(__FLI__, loop.target.id)

    # Create a stubber.
    stubber = LoopStubber(module)

    # Stub the loop invariant
    module = stubber.stub_loop_invariant(loop.body[0], loop, 'body', stub)

    # Print a separator.
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # Find all assignments.
    assignments_finder = AssignmentFinder()
    assignments_finder.visit(module)
    assignments = assignments_finder.find()

    for container, attr_name, ass in assignments:
        # Create a stub.
        ass_stub = create_ast_stub(__AS__, *[(target.id, str) for target in ass.targets],
                                   value=unparse(ass.value))

        # Create a stubber.
        ass_stubber = AssignmentStubber(module)

        # Stub.
        module = ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

    # Convert back to source.
    source_code = astor.to_source(module)

    # Print the source code.
    print(source_code)

    # Run it.
    exec(source_code)


if __name__ == '__main__':
    main()
