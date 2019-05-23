"""
    :file: engine.py
    :brief: Engine for PaLaDin Programming Language.
    :author: Oren Afek
    :since: 05/04/19
"""

import astor

from finders import *
from stubbers import *
from stubs import __AS__, __FLI__, create_ast_stub, archive, StubArgumentType


def create_ast(src_file) -> ast.AST:
    """
        Create an AST object out of a string of a source file.
    :param src_file: (str) A source file.
    :return: (Node) An AST node.
    """
    return ast.parse(src_file)


def loop_invariant_process(module):
    pidf = PaladinInlineDefinitionFinder()
    pidf.visit(module)
    loops = pidf.find()

    # Take the first loop.
    loop = [l for l in loops.keys()][0]

    # Create a stub.
    stub = create_ast_stub(__FLI__, [(loop.target.id, StubArgumentType.PLAIN)])

    # Create a stubber.
    stubber = LoopStubber(module)

    # Stub the loop invariant
    module = stubber.stub_loop_invariant(loop.body[0], loop, 'body', stub)


def main():
    # Read source file.
    with open(R'C:\Users\Owner\Documents\master\Project A\paladin_engine\PaladinEngine\Examples\Tetris\tetris.py') as f:
        tetris_source_file = f.read()

    module = create_ast(tetris_source_file)


    # Print a separator.
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # Find all assignments.
    assignments_finder = AssignmentFinder()
    assignments_finder.visit(module)
    assignments = assignments_finder.find()

    for container, attr_name, ass in assignments:
        # Create the list of the targets of the assignment.
        Assign()

        # Create a list for the assignment targets.
        targets = []

        class nameVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                targets.append([(node.id, StubArgumentType.NAME), (node.id, StubArgumentType.PLAIN)])
                self.generic_visit(node)

        for target in ass.targets:
            # Search for the targets in the left hand side of the assignment.
            nameVisitor().visit(target)

        # Create a stub.
        ass_stub = create_ast_stub(__AS__, *targets)

        # Create a stubber.
        ass_stubber = AssignmentStubber(module)

        # Stub.
        module = ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

    # Convert back to source.
    source_code = astor.to_source(module)

    # Print the source code.
    print(source_code)

    # Compile it.
    compiled_code = compile(source_code, r'C:\Users\Owner\AppData\Local\Temp\error', mode='exec')

    # Run it.
    exec(compiled_code, globals())

    # Print the archive.
    # print([(k, str(v)) for k, v in archive.all_values().items()])
    print(archive)

if __name__ == '__main__':
    main()
